from rita.controller import BaseFormController

class RestApiBaseController(BaseFormController):
    def _initialize(self):
        super(RestApiBaseController, self)._initialize()

    def getFormState(self):
        def validateToken():
            return not(self.session.sessionid != None and self.getParam("_rita_hidden_token") != self.session["_rita_hidden_token"])

        request_method = str(self.env["REQUEST_METHOD"]).upper()
        if request_method in ["DELETE"]:
            if validateToken():
                return self.FormState.DELETE_READY
        elif request_method in ["PUT", "POST"]:
            if validateToken() and self._validateForm():
                return self.FormState.INPUT_READY
        return self.FormState.INPUTTING
