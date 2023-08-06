from rita.controller import BaseFormController

class RestApiBaseController(BaseFormController):
    def _initialize(self):
        super(RestApiBaseController, self)._initialize()

    def get_form_state(self):
        request_method = str(self.env["REQUEST_METHOD"]).upper()
        if request_method in ["DELETE"]:
            if self._validate_hidden_token():
                return self.FormState.DELETE_READY
        elif request_method in ["PUT", "POST"]:
            if self._validate_hidden_token() and self._validate_form():
                return self.FormState.INPUT_READY
        return self.FormState.INPUTTING
