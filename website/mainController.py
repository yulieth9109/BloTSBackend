from flask import request, jsonify, Response, url_for, render_template, send_from_directory, json
import os, tempfile, base64
from os.path import join, dirname, realpath
from .dbManager import dbManager
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user
from .utilities import generate_confirmation_token, confirm_token, send_email

UPLOADS_PATH = join(dirname(realpath(__file__)), 'upload')

class mainController:

    @staticmethod
    def loginU(request):
        bodyData = request.json
        user = dbManager.getUserInfo(bodyData['Username'])
        if user:
            if check_password_hash(user.password, str(bodyData['Password'])) :
                login_user(user, remember=True)
                json_data = []
                content = {"Id": str(user.id), "FirstName": str(user.firstName), "LastName": str(user.lastName), "email" : user.email, "Role" : str(user.role)}
                json_data.append(content)
                return jsonify(json_data)
            else:
                return Response("Incorrect password, try again.", status = 400)
        else:
            return Response("Email does not exist, or your account is not active", status = 400)

    @staticmethod
    def signUp(request):
        urlS = request.url_root 
        id_number = request.form.get('IdNumber')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        date_of_birth = request.form.get('dateOfBirth')
        place_of_birth = request.form.get('placeOfBirth')
        phone_number = request.form.get('phoneNumber')
        countryP = request.form.get('countryPhone')
        postal_address = request.form.get('postalAddress')
        image = request.files['file']

        user = dbManager.checkUserE(email, id_number)
        if user :
            return Response("User already exist in the system", status=400)
        elif len(email) < 4:
            return Response("Email must be greater than 3 characters.", status=400)
        elif len(first_name) < 2:
            return Response("First name must be greater than 1 character.", status=400)
        elif password1 != password2:
            return Response("Passwords don\'t match.", status=400)
        elif len(password1) < 8 or len(password1) > 15:
            return Response("Password must be at least 8 characters and no more of 15 characters.", status=400)
        elif not id_number or not last_name or not date_of_birth or not place_of_birth or not phone_number or not countryP or not postal_address:
            return Response("Information Incomplete", status=400)
        elif image.filename == '' :
            return Response("Please provide a image of your ID", status=400)   
        else:
            filename = secure_filename(image.filename)
            new_user = dbManager.createUser(id_number, str(email), generate_password_hash(password1, method='sha256'),first_name, last_name, date_of_birth, countryP, place_of_birth, phone_number, postal_address, filename)
            if new_user == "OK":
                image.save(os.path.join(UPLOADS_PATH, 'DocumentsId',filename))    
                token = generate_confirmation_token(email.lower())
                confirm_url = url_for('routes.confirm_email', token=token, _external=True)
                html = render_template('activate.html', confirm_url=confirm_url, urlS = str(urlS))
                subject = "Please confirm your email"
                send_email(email, subject, html)
                return Response("A confirmation email has been sent via email.", status=200)
            else:
                return Response("ERR: Error with DB in the creation of the user, intent later", status=500)
    
    @staticmethod
    def confirmEmail(token):
        try:
            emailU = confirm_token(token,3600)
        except:
            return Response("The confirmation link is invalid or has expired.", status=400)
        user = dbManager.getUserInfo(emailU.lower())
        if user :
            return Response("Account already confirmed. Please login.", status=400)
        else:
            result = dbManager.activateAccount(emailU.lower())
            if result == "OK":
                return Response("You have confirmed your account. Please login", status=200)
            else:
                return Response("ERR: Error with DB in the activation of the account, intent later", status=500)

    @staticmethod
    def updateTestament(request):
        id_testator = request.form.get('IdNumberT')
        id_number_E = request.form.get('exIdNumber')
        first_name_E = request.form.get('exFirstName')
        last_name_E = request.form.get('exLastName')
        email_E = request.form.get('exEmail')
        postal_address_E = request.form.get('ExPostalAddress')
        countryP_E = request.form.get('exCountryPhone')
        phone_number_E = request.form.get('exPhoneNumber')
        testament = request.files['testament']
        sentEmail = 0
        hashT = ""
        executorStatus = ""

        if testament.filename == '' :
            return Response("Please provide your testament", status=400)
        else :
            user = dbManager.checkUserE("", id_testator)
            if user :
                if id_testator == id_number_E : 
                    return Response("The testator and the executor cannot be the same person", status=400)
                else :
                    #validate the existence of the Executor
                    executor = dbManager.validateExecutor(id_number_E, email_E)
                    if executor :
                        executorStatus = executor[0][2]
                        if executor[0][1] != email_E.lower() or str(executor[0][0]) != id_number_E : 
                            return Response("Your Executor already exist in the system but it has a different email or identification number, contact support service to solve the inconsistency", status=400)
                        if executor[0][2] == "PENDENT":
                            sentEmail = 1
                    else :
                        new_Executor = dbManager.createExecutor(id_number_E,first_name_E,last_name_E, email_E, postal_address_E,countryP_E,phone_number_E)
                        if new_Executor != "OK" :
                            return Response("ERR: Error in DB at the creation of executor data, intent later", status=500)
                        else: 
                            sentEmail = 1
        
                    #upload testament in the server

                    tf = "temporal/" + str(tempfile.NamedTemporaryFile()) + ".pdf"
                    testament.save(os.path.join(UPLOADS_PATH, tf)) 
        
                    #Validate the existence of metadataTestament

                    metadataTestament = dbManager.getTestamentMetadata(id_testator)
                    if metadataTestament:
                        hashT = metadataTestament[0][1]

                    #Create block information - Pendent definition of the information to keep in the blockchain

                    new_hash = generate_password_hash("testing", method='sha1')

                    if executorStatus == "PENDENT" or executorStatus == "" :
                        final_status = "EXECUTOR NOT CONFIRMED"
                    else : 
                        final_status = "COMPLETED"
     
                    if hashT == "" :
                        #create medataTestament
                        creationT =  dbManager.createMetadataT(id_testator, id_number_E, new_hash, final_status)
                        if creationT != "OK" :
                            return Response("ERR: Error in DB at the creation of testament data, intent later", status=500)
                    else :
                        #Update metadataTestament
                        updateT =  dbManager.updateMetadataT(id_testator, id_number_E, new_hash, final_status)
                        if updateT != "OK" :
                            return Response("ERR: Error in DB at the update of testament data, intent later", status=500)
                    
                    #Sent confimation email to the Executor

                    if sentEmail == 1 :
                        token = generate_confirmation_token(email_E.lower())
                        confirm_url = url_for('routes.confirm_email_executor', token=token, _external=True)
                        full_name = first_name_E + last_name_E
                        html = render_template('executorActivate.html', confirm_url = confirm_url, full_name = full_name)
                        subject = "Please confirm your email"
                        send_email(email_E, subject, html)

                    if final_status != "CONFIRMED" :
                        return Response("Your Testament has been storage, however It will not be valid until your executor confirm his/her email", status=200)
                    else :
                        return Response("Your Testament has been storage", status=200)

            else :
                return Response("Your Id Number does not exist in the system, contact support service", status=400)
 
    @staticmethod
    def confirmEmailExecutor(token):
        try:
            emailE = confirm_token(token,360000)
        except:
            return Response("The confirmation link is invalid or has expired.", status = 400)
        executor = dbManager.getExecutorInfo(emailE)
        if executor :
            return Response("Email already confirmed", status=400)
        else:
            result = dbManager.confirmExecutor(emailE)
            if result == "OK":
                result = dbManager.updateStatusTestament(emailE)
                if result == "OK":
                    return Response("You have confirmed your email", status=200)
                else :
                    return Response("ERR: Error with DB in the update of the testament, intent later", status=500)
            else:
                return Response("ERR: Error with DB in the confirmation of the email, intent later", status=500)

    @staticmethod
    def getBlockchainTestament(request):
        if len(request.get_data()) > 3 :
            bodyData = request.json
            print(bodyData['hashNumber'])

            #blockchain connection

            #retrieve of the testament

            #sending the testament
            return send_from_directory ( (os.path.join(UPLOADS_PATH, "temporal")) , "Testing Testament.pdf", as_attachment=False, etag = "NextHash=")
        else :
            return Response("Request without arguments", status=400)
        
    @staticmethod
    def requestRelease(request):
        idExecutorP = request.files['IdExecutor']
        certificateOfDeath = request.files['CertificatedDeath']

        extension = idExecutorP.filename.split('.')
        fp = next(tempfile._get_candidate_names()) + '.' + extension[len(extension) - 1]
        pathIdExecutorP = fp
        extension = certificateOfDeath.filename.split('.')
        fp = next(tempfile._get_candidate_names()) + '.' + extension[len(extension) - 1]
        pathDeathCertificate = fp

        if idExecutorP != '' and certificateOfDeath != '' and idExecutorP != certificateOfDeath:
            createRequest = dbManager.createRequest(pathIdExecutorP, pathDeathCertificate)
            if createRequest == "OK" :
                idExecutorP.save(os.path.join(UPLOADS_PATH,"Request", pathIdExecutorP)) 
                certificateOfDeath.save(os.path.join(UPLOADS_PATH,"Request", pathDeathCertificate)) 
                return Response("Your request has been created successfully, our team will make the validations and sent the response to the Executor's email")
            else :
                return Response("ERR: Error in DB in the creation of the request, intent later", status=500)
        else : 
            return Response("Provide a valid ID and certificate of death", status=400)
    
    @staticmethod
    def getListRequest():
        data = dbManager.getListRequest()
        if data :
            json_data = []
            for result in data:
                content = {"IdRequest": result[0], "TimeDateCreation": result[1]}
                json_data.append(content)
            print(json_data)
            return jsonify(json_data)
        else:
            return Response("There are not pendent request", status = 200)

    @staticmethod
    def getRequestInfo(request):
        bodyData = request.json
        requestData = dbManager.getRequestInfo(bodyData['idRequest'])
        if requestData:
            file = open(os.path.join(UPLOADS_PATH,"Request", requestData[0][1]), 'rb')
            file_read = file.read()
            IdExecutorP = base64.encodebytes(file_read)
            file = open(os.path.join(UPLOADS_PATH,"Request", requestData[0][2]), 'rb')
            file_read = file.read()
            DeathCertificate = base64.encodebytes(file_read)
            json_data = []
            content = {"IdRequest": requestData[0][0], "IdExecutorP": str(IdExecutorP), "DeathCertificate": str(DeathCertificate), "DateCreation" : requestData[0][4]}
            json_data.append(content)
            return jsonify(json_data)
        else :
            return Response("The request does not exist in the system", status = 400)
      
    @staticmethod
    def updateRequest(request):
        bodyData = request.json
        requestData = dbManager.getRequestInfo(str(bodyData['idRequest']))
        status = str(bodyData['status'])
        IdExecutor = str(bodyData['idExecutor'])
        IdTestator = str(bodyData['idTestator'])
        comments = str(bodyData['comments'])
        
        if str(status) == "APPROVED" :
            executor = dbManager.getExecutor(IdExecutor)
            if executor :
                TestamentData = dbManager.validateTestament(IdExecutor, IdTestator)
                if TestamentData :
                    update_request = dbManager.updateRequest(str(requestData[0][0]), "DOCUMENTS VALIDATED - APPROVED", comments, IdTestator)
                    if update_request == "OK" : 
                        token = generate_confirmation_token(IdTestator)
                        confirm_url = url_for('routes.confirm_release', token=token, _external=True)
                        full_name = executor[0][1] + executor[0][2]
                        testator_fullname = TestamentData[0][4] + TestamentData[0][5]
                        html = render_template('ReleaseConfirmation.html', confirm_url = confirm_url, full_name = full_name, testator_fullname = testator_fullname)
                        subject = "Confirmation Required"
                        send_email(executor[0][3], subject, html)
                        return Response("Request is approved, we sent an email to the executor for confirmation", status = 200)
                    else :
                        return Response("ERR: Error in DB in the update of the request, intent later", status = 500)
                else :
                    return Response("There is not a valid testament in the system to release", status = 400)
            else :
                return Response("Executor does not exist in the system or his/her status is not valid ", status = 400)
        elif str(status) == "DECLINED" :
            update_request = dbManager.updateRequest(str(requestData[0][0]), status, comments)
            if update_request == "OK" : 
                return Response("Request is declined", status = 200)
            else :
               return Response("ERR: Error in DB in the update of the request, intent later", status = 500) 
        else :
            return Response("To update the request provide a valid status", status = 400)

    @staticmethod
    def confirmRelease(token):

        try:
            IdTestator = confirm_token(token,360000)
        except:
            return Response("The confirmation link is invalid or has expired.", status = 400)
        testament = dbManager.getTestamentMetadata(IdTestator)
        if testament :
            hashB = testament[0][1]
        
            #retrieve data from blockchain
            # #reconstruc the document

            executor = dbManager.getExecutor(str(testament[0][0]))
            if executor :
                updateInfo = dbManager.updateTestament_Testator(IdTestator)
                if updateInfo == "OK" :
                    updateRequest = dbManager.updateRequestStatus(IdTestator, "PROCESSED")
                    if updateRequest == "OK" :
                        ## Sent link to qry   the testament - Sent an email with the testament
                        full_name = executor[0][1] + executor[0][2]
                        token = generate_confirmation_token(hashB)
                        confirm_url = url_for('routes.getTestamentLink', token=token, _external=True)
                        html = render_template('Release.html', confirm_url = confirm_url, full_name = full_name)
                        subject = "Testament Release"
                        testamentA = os.path.join(UPLOADS_PATH, "temporal", "Testing Testament.pdf")
                        send_email(str(executor[0][3]), subject, html, testamentA)
                        return render_template('message.html', message = "Testament release was successfull. Please check your email")
                    else :
                        return render_template('message.html', message = "ERR: Error in DB in the update of the request intent later or contact BloTs support")
                else :
                    return render_template('message.html', message = "ERR: Error in DB in the update of the testament intent later or contact BloTs support")
            else: 
                return render_template('message.html', message = "ERR: Executor information not found")
        else:
            return render_template('message.html', message = "Testament does not exist in the system, contact support")
    
    @staticmethod
    def getBlockchainTestamentL(token) :
        try:
            HashB = confirm_token(token,360000)

            #blockchain connection

            #retrieve of the testament

            #sending the testament
            return send_from_directory ( (os.path.join(UPLOADS_PATH, "temporal")) , "Testing Testament.pdf", as_attachment=False, etag = "NextHash=")
        except:
            return Response("The confirmation link is invalid or has expired.", status = 400)

        