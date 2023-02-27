from flask import request, jsonify, Response, url_for, render_template, send_from_directory, json
import os, tempfile, base64, requests, json, hashlib
from os.path import join, dirname, realpath
from .dbManager import dbManager
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user
from .utilities import generate_confirmation_token, confirm_token, send_email, sendTransactionBl, getTransactionBl
import website.parameters as parameters

UPLOADS_PATH = join(dirname(realpath(__file__)), 'upload')
urlS = "https://pristine-dahlia-377509.ey.r.appspot.com/"

class mainController:
    
    @staticmethod
    def loginU(request):
        global urlS
        bodyData = request.json
        user = dbManager.getUserInfo(bodyData['Username'])
        if user:
            if check_password_hash(user.password, str(bodyData['Password'])) :
                login_user(user)
                json_data = []
                content = {"Id": str(user.tid), "FirstName": str(user.firstName), "LastName": str(user.lastName), "email" : user.email, "Role" : str(user.role)}
                json_data.append(content)
                return jsonify(json_data)
            else:
                return Response("Incorrect password, try again.", status = 400)
        else:
            return Response("Email does not exist, or your account is not active", status = 400)

    @staticmethod
    def signUp(request):
        global urlS
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
                return Response("ERR: Error with DB in the creation of the user, try later", status=500)
    
    @staticmethod
    def confirmEmail(token):
        global urlS
        try:
            emailU = confirm_token(token,3600)
        except:
            return render_template('message.html', message="The confirmation link is invalid or has expired.", urlS = str(urlS))
            
        user = dbManager.getUserInfo(emailU.lower())
        if user :
            return render_template('message.html', message = "Account already confirmed. Please login.", urlS = str(urlS))
        else:
            result = dbManager.activateAccount(emailU.lower())
            if result == "OK":
                return render_template('message.html', message = "You have confirmed your account. Please login", urlS = str(urlS))
            else:
                return render_template('message.html', message = "ERR: Error with DB in the activation of the account, try later", urlS = str(urlS))

    @staticmethod
    def updateTestament(request):
        global urlS
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
        blockChainERR = 0
        hashT = ""
        executorStatus = ""

        if testament.filename == '' :
            return Response("Please provide your testament", status=400)
        else :
            user = dbManager.checkUserE("", id_testator)
            if user :
                if id_testator == id_number_E : 
                    return Response("The testator and the executor cannot be the same person", status=400)
                else:
                    try :
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
                                return Response("ERR: Error in DB at the creation of executor data, try later", status=500)
                            else: 
                                sentEmail = 1
            
                        #upload testament in the server

                        tf = str(next(tempfile._get_candidate_names())) + ".pdf"
                        testament.save(os.path.join(UPLOADS_PATH, "temporal", tf)) 
            
                        #Validate the existence of metadataTestament

                        metadataTestament = dbManager.getTestamentMetadata(id_testator)
                        if metadataTestament:
                            hashT = metadataTestament[0][1]

                        #Convert the document in Base64 - create file in IFPS Infura
                        file = open(os.path.join(UPLOADS_PATH, "temporal", tf), 'rb')
                        file_read = file.read()
                        testamentD = base64.encodebytes(file_read)
                        sTestamentD = testamentD.decode('utf-8')

                        endpoint = parameters.infuraEn
                        files = {'file': sTestamentD[50:]}
                        response = requests.post(endpoint + '/api/v0/add', files = files, auth=(parameters.infuraP, parameters.infuraPS))
                        p = response.json()
                        hashI = p['Hash']
                        
                        #blockinformation: Id Testator  + First 50 charactects of the base64 string + hash256 of the testament + '.' + infurahash + '.' previus hash
                        sha256hash = hashlib.sha256(file_read).hexdigest()
                        nextHash = ""
                        if hashT == "":
                            nextHash = "-"
                        else:
                            nextHash = hashT
                        msg = str(id_testator) + '*.*' + str(sTestamentD[0:50]  + '*.*' + str(sha256hash) + '*.*' + str(hashI) + '*.*' + str(nextHash))
                        #print("This is the block information " + str(msg))

                        os.remove(os.path.join(UPLOADS_PATH, "temporal", tf))
                        
                        new_hash = sendTransactionBl(msg)
                        typeV = str(type(new_hash))

                        if 'str' not in typeV : 
                            new_hash = new_hash.hex()
                        else:
                            return Response("ERR: Communication with Blockchain not successful. Try later", status = 500)

                        if executorStatus == "PENDENT" or executorStatus == "" :
                            final_status = "EXECUTOR NOT CONFIRMED"
                        else : 
                            final_status = "COMPLETED"
        
                        if hashT == "" :
                            #create medataTestament
                            creationT =  dbManager.createMetadataT(id_testator, id_number_E, new_hash, hashI, final_status)
                            if creationT != "OK" :
                                return Response("ERR: Error in DB at the creation of testament data, try later", status=500)
                        else :
                            #Update metadataTestament
                            updateT =  dbManager.updateMetadataT(id_testator, id_number_E, new_hash, hashI, final_status)
                            if updateT != "OK" :
                                return Response("ERR: Error in DB at the update of testament data, try later", status=500)
                        
                        #Sent confimation email to the Executor

                        if sentEmail == 1 :
                            token = generate_confirmation_token(email_E.lower())
                            confirm_url = url_for('routes.confirm_email_executor', token=token, _external=True)
                            full_name = first_name_E + last_name_E
                            html = render_template('executorActivate.html', confirm_url = confirm_url, full_name = full_name, urlS = str(urlS))
                            subject = "Please confirm your email"
                            send_email(email_E, subject, html)

                        if final_status != "COMPLETED" :
                            return Response("Your Testament has been storage, however It will not be valid until your executor confirm his/her email", status=200)
                        else :
                            return Response("Your Testament has been storage", status=200)

                    except Exception as e :
                        print(e)
                        return Response(" Unexpected error, try later ", status = 500)
            else :
                return Response("Your Id Number does not exist in the system, contact support service", status=400)
 
    @staticmethod
    def confirmEmailExecutor(token):
        global urlS
        try:
            emailE = confirm_token(token,360000)
        except:
            return render_template('message.html', message = "The confirmation link is invalid or has expired.", urlS = str(urlS))
            
        executor = dbManager.getExecutorInfo(emailE)

        if executor :
            return render_template('message.html', message = "Email already confirmed.", urlS = str(urlS))
        else:
            result = dbManager.confirmExecutor(emailE)
            if result == "OK":
                result = dbManager.updateStatusTestament(emailE)
                if result == "OK":
                    return render_template('message.html', message = "You have confirmed your email.", urlS = str(urlS))
                else :
                    return render_template('message.html', message = "ERR: Error with DB in the update of the testament, try later", urlS = str(urlS))
            else:
                return render_template('message.html', message = "Error with DB in the confirmation of the email, try later", urlS = str(urlS))

    @staticmethod
    def getBlockchainTestament(request):
        global urlS
        if len(request.get_data()) > 3 :
            bodyData = request.json
            hashNumber = bodyData['hashNumber']
            data = Additional.buildTestament(hashNumber)
            typeV = str(type(data))
            if 'str' not in typeV:
                return send_from_directory((os.path.join(UPLOADS_PATH, "temporal")) , str(hashNumber) + ".PDF", as_attachment=False, etag = "NextHash=" + str(data.nextHash))
            else :
                return Response(data, status = 500)
        else :
            return Response("Request without arguments", status=400)
        
    @staticmethod
    def requestRelease(request):
        global urlS
        idExecutorP = request.files['IdExecutor']
        certificateOfDeath = request.files['CertificatedDeath']

        extension = idExecutorP.filename.split('.')
        fp = next(tempfile._get_candidate_names()) + '.' + extension[len(extension) - 1]
        pathIdExecutorP = fp
        extension = certificateOfDeath.filename.split('.')
        fp = next(tempfile._get_candidate_names()) + '.' + extension[len(extension) - 1]
        pathDeathCertificate = fp

        if idExecutorP.filename!= '' and certificateOfDeath.filename != '' and idExecutorP.filename != certificateOfDeath.filename:
            createRequest = dbManager.createRequest(pathIdExecutorP, pathDeathCertificate)
            if createRequest == "OK" :
                idExecutorP.save(os.path.join(UPLOADS_PATH,"Request", pathIdExecutorP)) 
                certificateOfDeath.save(os.path.join(UPLOADS_PATH,"Request", pathDeathCertificate)) 
                return Response("Your request has been created successfully, our team will make the validations and sent the response to the Executor's email")
            else :
                return Response("ERR: Error in DB in the creation of the request, try later", status=500)
        else : 
            return Response("Provide a valid ID and certificate of death", status=400)
    
    @staticmethod
    def getListRequest():
        global urlS
        data = dbManager.getListRequest()
        if data :
            json_data = []
            for result in data:
                content = {"IdRequest": result[0], "TimeDateCreation": result[1]}
                json_data.append(content)
            return jsonify(json_data)
        else:
            return Response("There are not pendent request", status = 200)

    @staticmethod
    def getRequestInfo(request):
        global urlS
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
            content = {"IdRequest": requestData[0][0], "IdExecutorN": requestData[0][1],"IdExecutorP": str(IdExecutorP), "DeathCertificateN": requestData[0][2], "DeathCertificate": str(DeathCertificate), "DateCreation" : requestData[0][4]}
            json_data.append(content)
            return jsonify(json_data)
        else :
            return Response("The request does not exist in the system", status = 400)
      
    @staticmethod
    def updateRequest(request):
        global urlS
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
                        testator_fullname = TestamentData[0][4] + " " + TestamentData[0][5]
                        html = render_template('ReleaseConfirmation.html', confirm_url = confirm_url, full_name = full_name, testator_fullname = testator_fullname, urlS = str(urlS))
                        subject = "Confirmation Required"
                        send_email(executor[0][3], subject, html)
                        return Response("Request is approved, we sent an email to the executor for confirmation", status = 200)
                    else :
                        return Response("ERR: Error in DB in the update of the request, try later", status = 500)
                else :
                    return Response("There is not a valid testament in the system to release", status = 400)
            else :
                return Response("Executor does not exist in the system or his/her status is not valid ", status = 400)
        elif str(status) == "DECLINED" :
            update_request = dbManager.updateRequest(str(requestData[0][0]), status, comments)
            if update_request == "OK" : 
                return Response("Request is declined", status = 200)
            else :
               return Response("ERR: Error in DB in the update of the request, try later", status = 500) 
        else :
            return Response("To update the request provide a valid status", status = 400)

    @staticmethod
    def confirmRelease(token):
        global urlS
        try:
            IdTestator = confirm_token(token, 360000)
        except : 
            return render_template('message.html', message = "The confirmation link is invalid or has expired.", urlS = str(urlS))
        
        if IdTestator != False :
            testament = dbManager.getTestamentMetadata(IdTestator)
            if testament :
                hashB = testament[0][1]
                data = Additional.buildTestament(hashB)
                typeV = str(type(data))

                if 'str' not in typeV:
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
                                html = render_template('Release.html', confirm_url = confirm_url, full_name = full_name, urlS = str(urlS))
                                subject = "Testament Release"
                                hashFile = str(hashB) + ".PDF"
                                testamentA = os.path.join(UPLOADS_PATH, "temporal", hashFile)
                                send_email(str(executor[0][3]), subject, html, testamentA)
                                return render_template('message.html', message = "Testament release was successfull. Please check your email", urlS = str(urlS))
                            else :
                                return render_template('message.html', message = "ERR: Error in DB in the update of the request try later or contact BloTs support", urlS = str(urlS))
                        else :
                            return render_template('message.html', message = "ERR: Error in DB in the update of the testament try later or contact BloTs support", urlS = str(urlS))
                    else: 
                        return render_template('message.html', message = "ERR: Executor information not found", urlS = str(urlS))
                else :
                    return Response(data, status = 500)
            else:
                return render_template('message.html', message = "Testament does not exist in the system, contact support", urlS = str(urlS))
        else:
             return render_template('message.html', message = "The confirmation link is invalid.", urlS = str(urlS))

    @staticmethod
    def getBlockchainTestamentL(token):
        global urlS
        try:
            HashB = confirm_token(token, 360000)
            
            if HashB != False :
                data = Additional.buildTestament(HashB)
                typeV = str(type(data))

                if 'str' not in typeV:
                    return send_from_directory((os.path.join(UPLOADS_PATH, "temporal")) , str(HashB) + ".PDF", as_attachment=False)
                else :
                    return render_template('message.html', message=data)
            else:
                return render_template('message.html', message = "The confirmation link is invalid.")
        except Exception as e:
            print(e)
            return render_template('message.html', message = "The confirmation link is invalid or has expired.")
        
    @staticmethod
    def getTestamentHash(request):
        global urlS
        bodyData = request.json
        requestData = dbManager.getTestamentHash(bodyData['IdTestator'])
        if requestData:
            json_data = []
            content = {"Hash": requestData[0][0]}
            json_data.append(content)
            return jsonify(json_data)
        else :
            return Response("The user does not have wills", status=400)

class Additional:

    @staticmethod
    def buildTestament(txnHash):
        infoTest = getTransactionBl(txnHash)
        typeV = str(type(infoTest))

        if 'str' not in typeV:
            message = infoTest["newMessage"]
            valuesBl = message.split('*.*')
            #get infura data
            pathI = (os.path.join(UPLOADS_PATH, "temporal", txnHash + ".PDF"))
            params = (('arg', valuesBl[3]), ('output', pathI ))
            endpoint = parameters.infuraEn
            responseI = requests.post(endpoint + '/api/v0/cat', params = params, auth=(parameters.infuraP, parameters.infuraPS))

            if responseI.status_code == 200:

                base64Testament = str(valuesBl[1]) + str(responseI.text)
                base64_bytes = base64Testament.encode('utf-8')
                message_bytes = base64.decodebytes(base64_bytes)
                sha256hash = hashlib.sha256(message_bytes).hexdigest()

                if sha256hash == valuesBl[2]:
                    # Write the file contents in the response to a file specified by local_file_path
                    finalT= open(pathI,"wb")
                    finalT.write(message_bytes)
                    finalT.close()
                    responseData = responseD(finalT, valuesBl[4])
                    return responseData
                else:
                    return "Your Testament present inconsistency in the system, please call support. "
            else:
                return "Connection to our external IPFS provider not possible at this momment, please try later. "
        else:
            return infoTest

class responseD ():
  def __init__(self, file, nextHash):
    self.file = file
    self.nextHash = nextHash  

        