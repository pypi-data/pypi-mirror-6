from lizard import CodeReader


class PythonReader(CodeReader):

    ext = ['py']
    conditions = set(['if', 'for', 'while', 'and', 'or', 'elif', 'except', 'finally'])

    def __init__(self):
        self._state = self._GLOBAL
        self.function_stack = []
        self.current_indent = 0
        self.leading_space = True

    @staticmethod
    def generate_tokens(source_code):
        return CodeReader.generate_tokens(source_code, r"|\'\'\'.*?\'\'\'" + r'|\"\"\".*?\"\"\"')

    def preprocess(self, tokens, context):
        for token in tokens:
            if token != '\n':
                if self.leading_space:
                    if token.isspace():
                        self.current_indent = len(token.replace('\t', ' ' * 8))
                    else:
                        if not token.startswith('#'):
                            self._close_functions()
                        self.leading_space = False
            else:
                self.leading_space = True
                self.current_indent = 0
            if not token.isspace() or token == '\n':
                yield token

    @staticmethod
    def get_comment_from_token(token):
        if token.startswith("#"):
            return token[1:]

    def _GLOBAL(self, token):
        if token == 'def':
            self._state = self._FUNCTION

    def _FUNCTION(self, token):
        if token != '(':
            self.function_stack.append(self.context.current_function)
            self.context.START_NEW_FUNCTION(token)
            self.context.current_function.indent = self.current_indent
        else:
            self._state = self._DEC

    def _DEC(self, token):
        if token == ')':
            self._state = self._GLOBAL
        else:
            self.context.PARAMETER(token)
            return
        self.context.ADD_TO_LONG_FUNCTION_NAME(" " + token)

    def eof(self):
        self.current_indent = 0
        self._close_functions()

    def _close_functions(self):
        while self.context.current_function.indent >= self.current_indent:
            endline = self.context.current_function.end_line
            self.context.END_OF_FUNCTION()
            self.context.current_function = self.function_stack.pop()
            self.context.current_function.end_line = endline
