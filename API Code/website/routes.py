from flask import Blueprint,request
from flask_login import current_user, login_required, login_user, logout_user
from .mainController import mainController

routes = Blueprint('routes', __name__)

mainControllerC = mainController()


@routes.route('/login', methods=['POST'])
def login():
    return mainControllerC.loginU(request)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return "Loging out"


@routes.route('/sign-up', methods=['POST'])
def sign_up():
    return mainControllerC.signUp(request)

@routes.route('/confirm/<token>')
def confirm_email(token):
    return mainControllerC.confirmEmail(token)

@routes.route('/confirmE/<token>')
def confirm_email_executor(token):
    return mainControllerC.confirmEmailExecutor(token)

@routes.route('/updateTestament', methods=['POST'])
@login_required
def updateTestament():
    return mainControllerC.updateTestament(request)

@routes.route('/getTestamentHash', methods=['POST'])
@login_required
def getTestamentHash():
    return mainControllerC.getTestamentHash(request)

@routes.route('/getTestament', methods=['POST'])
@login_required
def getTestament():
    return mainControllerC.getBlockchainTestament(request)

@routes.route('/requestRelease', methods=['POST'])
def requestRelease():
    return mainController.requestRelease(request)

@routes.route('/getListRequest', methods=['GET'])
@login_required
def getListRequest():
    return mainControllerC.getListRequest()

@routes.route('/getRequestInfo', methods=['POST'])
@login_required
def getRequestInfo():
    return mainControllerC.getRequestInfo(request)

@routes.route('/updateRequest', methods=['POST'])
@login_required
def updateRequest() :
    return mainControllerC.updateRequest(request)

@routes.route('/confirmR/<token>')
def confirm_release(token):
    return mainControllerC.confirmRelease(token)

@routes.route('/getTestamentLink/<token>')
def getTestamentLink(token):
    return mainControllerC.getBlockchainTestamentL(token)