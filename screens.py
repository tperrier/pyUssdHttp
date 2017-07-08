import collections
from . import utils
from back import back_button


class BaseScreen(object):

    body = "None"
    _has_next = False
    next_screen = None

    def __init__(self,body=None,has_next=None,next_screen=None):
        if body is not None:
            self.body = body
        if has_next is not None:
            self._has_next = False
        if next_screen is not None:
            self.next_screen = next_screen
        else:
            self.next_screen = self.get_next_screen()

    def has_next(self,session):
        return bool(self._has_next) or self.next_screen is not None

    def render(self,session,context):
        try:
            return self.body.format(**context)
        except TypeError as e:
            return self.body

    def input(self,input,session,context):
        """ Process input for screen
            return: ScreenResult (next_screen , valid , output )
        """
        return BaseScreen("None") if self.next_screen is None else self.next_screen

    def get_next_screen(self):
        return self.next_screen

    def note(self):
        ''' this is added to the log when this screen is displayed'''
        if self.body == 'None': return self.__name__
        else: return self.body

    ########################################
    # Static Factory Methods
    ########################################

    @classmethod
    def no_next(cls,label):
        return cls("%s Has No Next Action"%label)

def _validate_render(func):
    def wrapper(self,session,context):
        if session[self.VALIDATION_ERROR] is not None:
            return session[self.ERROR_MSG]
        return func(self,session,context)
    return wrapper

class InputScreen(BaseScreen):

    VALIDATION_ERROR = 'has_exception'
    ERROR_MSG = 'exception_text'

    body = "Input Text"
    exception_type = Exception
    error_msg = "Validation Error on {input}"
    _has_next = True


    @_validate_render
    def render(self,session,context):
        return super(InputScreen,self).render(session,context)

    def input(self,input,session,context):
        try:
            # Attempt to validate input
            action_next = self.action(input,session,context)
        except self.exception_type as e:
            # If validation fails set error message and return self
            session[self.VALIDATION_ERROR] = True
            session[self.ERROR_MSG] = self.error_msg.format(input=input,error=e)
            return self
        if session[self.VALIDATION_ERROR] is not None:
            del session[self.VALIDATION_ERROR]

        if isinstance(action_next,BaseScreen):
            return action_next

        return self.next_screen if self.next_screen is not None else \
            BaseScreen("Input: {} Validated: {}".format(input,validated_input))

    def action(self,input,context):
        # Default clean method
        return input

    @staticmethod
    def validate_render(func):
        return _validate_render(func)

class MenuScreen(InputScreen):

    exception_type = (ValueError,IndexError)

    @property
    def error_msg(self):
        return "{{input}} must be between 1 and {}".format(len(self.menu_items))

    def __init__(self,title="Select One",items=None):
        self.title_str = title
        self.menu_items = []
        self.add_items(items)

    @InputScreen.validate_render
    def render(self,session,context):
        menu = [] if self.title_str == '' else ["   %s" % self.title_str]
        for idx , item in enumerate(self.menu_items):
            menu_text = "%i. %s"%(idx+1,item) if not item.hide_index else str(item)
            menu.append( menu_text )
        return "\n".join(menu)

    def action(self,input,session,context):
        """ Return next menu screen or error message """
        index = int(input) - 1
        if index < 0:
            raise IndexError('Menu option can not be less than 1')
        return self.menu_items[index].next_screen

    def add_items(self,items):
        if items is None:
            return # Do nothing
        elif utils.not_iterable(items):
            self.append( item )
        else:
            for item in items:
                self.append( item )

    def append(self,item):
        if not isinstance(item,MenuItem):
            item = MenuItem(item)
        self.menu_items.append(item)

    def note(self):
        """ overriding logging notes here """
        return self.title_str

class MenuItem(object):
    """ Object representing a menu option label and next_screen if selected """

    def __init__(self,label,next_screen=None, hide_index=False):
        if utils.not_iterable(label):
            self.label = str(label)
            self.next_screen = next_screen if next_screen is not None else BaseScreen.no_next(self.label)
        else:
            self.label = str(label[0])
            self.next_screen = label[1] if len(label) > 1 else None
            if not isinstance(self.next_screen,BaseScreen):
                self.next_screen = BaseScreen.no_next(self.next_screen)

        self.hide_index = hide_index

    def __str__(self):
        return self.label

class LongMenuScreen(MenuScreen):
    """ adds items until 160 chars are taken up, then puts
        the rest in a submenu titled 'next'. """
    overflow_str = 'next, {}. back'.format(back_button)
    back_str = "{}. Back".format(back_button)

    def __init__(self, title="Select One", items=None, show_back=True, shift=0):
        self.title_str = title
        self.menu_items = []
        self.cutoff_len = 140 # a margin of error here

        self.shift = shift

        def current_length():
            title_len = len(self.title_str) + 4
            item_len = sum(map(lambda x: len(str(x)), self.menu_items))
            numeral_len = 4 * len(self.menu_items)
            back_len = len(self.back_str) if show_back else 0
            return sum((title_len, item_len, numeral_len, back_len))


        i = 0
        while current_length() < self.cutoff_len-len(self.overflow_str) and i<len(items):
            # ^ this accounts for the last menu item in calculations
            #TODO: this logic isn't perfect, as if there's only one more item left,
            # we can fit it on a single screen if it keeps len < 160 chars
            self.menu_items.append(MenuItem(items[i]))
            i +=1

        if i == len(items):
            # we can fit all on this page, so let's add the back_str if needed
            if show_back:
                self.menu_items.append(MenuItem(self.back_str, hide_index=True))
                # this is a bit hacky since it doesn't use the BaseScreen
                # instead relies on sessions to catch the back key

        else:
            # we need an overflow page
            overflow_item = MenuItem(self.overflow_str,
                             LongMenuScreen(title, items[i:], shift=i))

            self.menu_items.append(overflow_item)

    @InputScreen.validate_render
    def render(self,session,context):
        """ I'm overriding this here so that we can shift the index for subsequent
            pages."""
        #TODO: at some point this should actually get implemented, but to do so
        # would need to convert self.menu_items from list to a dict, where the
        # keys are the items that should be selected in the menu. 
        # to do so would need to update MenuItem as well.
        menu = [] if self.title_str == '' else ["   %s" % self.title_str]
        for idx , item in enumerate(self.menu_items):
            if item.hide_index: menu_text = str(item)
            else:
                #menu_text = "%i. %s"%(idx + self.shift + 1, item)
                menu_text = "%i. %s"%(idx + 1, item)
            menu.append( menu_text )
        return "\n".join(menu)


class QuestionScreen(InputScreen):

    _has_next = True
    name = "question"

    def __init__(self,question=None,name=None,exception_type=None,error_msg=None,next_screen=None):
        if question is not None:
            self.question = question
        if name is not None:
            self.name = name
        if exception_type is not None:
            self.exception_type = exception_type
        if error_msg is not None:
            self.error_msg = error_msg
        super(QuestionScreen,self).__init__(next_screen=next_screen)

    @property
    def body(self):
        return self.question

    def action(self,input,session,context):
        session[self.name] = self.validate(input)

    def validate(self,input):
        return input

class FloatQuestion(QuestionScreen):

    error_msg = "{input} is not a float"
    exception_type = ValueError

    def validate(self,input):
        return float(input)

class IntegerQuestion(QuestionScreen):

    error_msg = "{input} is not a int"
    exception_type = ValueError

    def validate(self,input):
        return int(input)

class SelectOne(QuestionScreen):

    labels = ['One','Two','Three']
    values = [1,2,3]
    error_msg = "{{input}} must be between 1 and {}".format(len(values))
    exception_type = (ValueError,IndexError)

    def __init__(self,name=None,exception_type=None,error_msg=None,next_screen=None,labels=None,values=None,lookups=None):
        if labels is not None:
            self.labels = labels
        if values is not None:
            self.values = values
        if lookups is not None:
            self.value_lookup = lookups
        if not hasattr(self,'label_lookup'):
            self.label_lookup = [ label.lower() for label in self.labels ]
        super(SelectOne,self).__init__(name=name,exception_type=exception_type,error_msg=error_msg,next_screen=next_screen)

    @property
    def body(self):
        output = ['  Select One']
        for idx , label in enumerate(self.labels):
            output.append( "{}. {}".format(idx+1,label) )
        return "\n".join(output)

    def validate(self,input):
        if input.lower() in self.label_lookup:
            # Input is label. Return value for label.
            value_idx = self.label_lookup.index(input.lower())
            return SelectItem(self.labels[value_idx],self.values[value_idx])
        # Otherwise assume that index is an int in range len(self.values)
        idx = int(input) - 1
        return SelectItem(self.labels[idx],self.values[idx])

SelectItem = collections.namedtuple('SelectItem',['label','value'])

class ValidationError(Exception):
    pass
