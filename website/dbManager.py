import mysql.connector, datetime
from.User import User
from mysql.connector import Error
import website.parameters as parameters

class ConexionDB:
    
    def executeQry(qryString, Operation) :
        result = ''
        try:
            connection = mysql.connector.connect(host = parameters.hostDB, database = parameters.database, user = parameters.userDB, password = parameters.passwordDB)
            if connection.is_connected() :
                cursor = connection.cursor()
                cursor.execute(qryString)
                #print("Execute Qry" + qryString)
                if Operation == "QRY" :
                    result = cursor.fetchall()
                elif Operation == "INSERT" :
                    connection.commit()
                    result = "OK"   
        except Error as e:
            print("Error while connecting to MySQL", e)
            result = "Error while connecting to MySQL"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close() 
            return result


class dbManager:

    @staticmethod
    def getUserInfo(email) :
        qry = "SELECT `FirstName`,`LastName`,`Email`, `Password`, `Role`, `idNumber` FROM `testament_manager`.`user` WHERE email='" + email.lower() + "' AND Status = 'ACTIVE'"
        result = ConexionDB.executeQry(qry,"QRY")
        print("Email " + str(email))
        if result:
            print("Users " + str(result))
            user = User(result[0][5], result[0][2], result[0][0], result[0][1], result[0][3], result[0][4])
            print(user.email)
            return user
        else:
            return None

    @staticmethod
    def checkUserE(email, id_number) :
        qry = "SELECT Email FROM `testament_manager`.`user` WHERE email='" + email.lower() + "' OR idNumber = '" + id_number + "'"
        result = ConexionDB.executeQry(qry,"QRY")
        return result

    @staticmethod
    def createUser(id_number, email, password, first_name, last_name, date_of_birth, countryP, place_of_birth, phone_number, postal_address, id_image) :
        date_creation = str(datetime.datetime.now())
        qry = "INSERT INTO `testament_manager`.`user` (`idNumber`, `FirstName`,`LastName`,`Email`,`Password`,`Role`, `Status`, `DateBirth`, `PlaceBirth`, `CountryCodeP`, `PhoneNumber`, `IdImage`,`PostalAddress`, `DateCreation`) VALUES('" + id_number + "', '" + first_name + "','" + last_name + "','" + email.lower() + "','" + password + "', 'USER  ', 'PENDENT', '" + date_of_birth + "' , '" + place_of_birth + "' , '" + countryP + "' , '" + phone_number + "' , '" + id_image + "' , '" + postal_address + "' , '" + date_creation + "' )"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result
    
    @staticmethod
    def activateAccount(email) :
        date_last_updated = str(datetime.datetime.now())
        qry = "UPDATE `testament_manager`.`user` SET Status = 'ACTIVE', DateLastModification = '" + date_last_updated + "' WHERE email='" + email.lower() + "'"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result
    
    @staticmethod
    def validateExecutor(idExecutor, email) :
        qry = "SELECT IdNumberE, Email, Status FROM `testament_manager`.`executor` WHERE Email='" + email.lower() + "' OR IdNumberE = '" + idExecutor + "'"
        result = ConexionDB.executeQry(qry,"QRY")
        return result
    
    @staticmethod
    def createExecutor(id_number, first_name, last_name,  email, postal_address, countryP, phone_number) :
        date_creation = str(datetime.datetime.now())
        qry = "INSERT INTO `testament_manager`.`executor` (`IdNumberE`, `FirstName`,`LastName`,`Email`, `PostalAddress`, `CountryCodeP`, `PhoneNumber`, `Status`, `DateCreation`) VALUES('" + id_number + "', '" + first_name + "','" + last_name + "','" + email.lower() + "', '" + postal_address + "', '" + countryP + "' , '" + phone_number + "' ,'PENDENT', '" + date_creation + "' )"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result
    
    @staticmethod
    def getTestamentMetadata(idTestator) :
        qry = "SELECT IdExecutor, Hash, Status FROM `testament_manager`.`metadataTestament` WHERE IdTestator='" + idTestator + "'"
        result = ConexionDB.executeQry(qry,"QRY")
        return result
    
    @staticmethod
    def createMetadataT(id_testator, id_executor, new_hash, status) :
        date_creation = str(datetime.datetime.now())
        qry = "INSERT INTO `testament_manager`.`metadataTestament` (`IdTestator`, `IdExecutor`,`Hash`,`Status`, `DateCreation`) VALUES('" + id_testator + "', '" + id_executor + "','" + new_hash + "' ,'" +  status + "', '" + date_creation + "' )"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result
    
    @staticmethod
    def updateMetadataT(id_testator, id_executor, new_hash, status) :
        date_last_updated = str(datetime.datetime.now())
        qry = "UPDATE `testament_manager`.`metadataTestament` SET IdExecutor = '" + id_executor + "', Hash = '" + new_hash + "', Status = '" + status +"', DateLastModification = '" + date_last_updated + "' WHERE IdTestator='" + id_testator + "'"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result
    
    @staticmethod
    def getExecutorInfo(email) :
        qry = "SELECT IdNumberE, Email, Status FROM `testament_manager`.`executor` WHERE Email='" + email.lower() + "' AND Status = 'CONFIRMED'"
        result = ConexionDB.executeQry(qry,"QRY")
        return result
    
    @staticmethod
    def confirmExecutor(EmailE) :
        date_last_updated = str(datetime.datetime.now())
        qry = "UPDATE `testament_manager`.`executor` SET Status = 'CONFIRMED', DateLastModification = '" + date_last_updated + "' WHERE Email='" + EmailE.lower() + "'"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result
    
    @staticmethod
    def updateStatusTestament(EmailE) :
        date_last_updated = str(datetime.datetime.now())
        qry = "UPDATE `testament_manager`.`metadataTestament` AS T1 INNER JOIN `testament_manager`.`executor` AS T2 ON T1.IdExecutor = T2.IdNumberE SET T1.Status = 'COMPLETED', T1.DateLastModification = '" + date_last_updated + "' WHERE T2.Email='" + EmailE + "'"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result
    
    @staticmethod
    def createRequest(pathIdExecutorP, pathDeathCertificate) :
        date_creation = str(datetime.datetime.now())
        qry = "INSERT INTO `testament_manager`.`request` (`IdExecutorP`, `DeathCertificate`,`Status`, `DateCreation`) VALUES('" + pathIdExecutorP + "', '" + pathDeathCertificate + "', 'PENDENT', '" + date_creation + "' )"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result
    
    @staticmethod
    def getListRequest() :
        qry = "SELECT IdRequest, DATE_FORMAT(DateCreation, '%d/%m/%Y %H:%i') FROM `testament_manager`.`request` WHERE Status = 'PENDENT'"
        result = ConexionDB.executeQry(qry,"QRY")
        return result
    
    @staticmethod
    def getRequestInfo(IdRequest) :
        qry = "SELECT `IdRequest`, `IdExecutorP`, `DeathCertificate`,`Status`, DATE_FORMAT(DateCreation, '%d/%m/%Y %H:%i') FROM `testament_manager`.`request` WHERE IdRequest = '"+ IdRequest + "'"
        result = ConexionDB.executeQry(qry,"QRY")
        return result
    
    @staticmethod
    def validateTestament(IdExecutor, IdTestator) :
        qry = "SELECT IdTestator, IdExecutor, Hash, T1.Status, FirstName, LastName FROM `testament_manager`.`metadataTestament`AS T1 INNER JOIN `testament_manager`.`user` AS T2 ON T1.IdTestator = T2.idNumber  WHERE IdTestator='" + IdTestator + "' AND IdExecutor = '" + IdExecutor + "' AND T1.Status = 'COMPLETED'"
        result = ConexionDB.executeQry(qry,"QRY")
        return result
    
    @staticmethod
    def getExecutor(IdExecutor) :
        qry = "SELECT IdNumberE, FirstName, LastName, Email, Status FROM `testament_manager`.`executor` WHERE IdNumberE = '" + IdExecutor + "' AND Status = 'CONFIRMED'"
        result = ConexionDB.executeQry(qry,"QRY")
        return result
    
    @staticmethod
    def updateRequest(IdRequest, Status, Comments, IdTestament = None) :
        date_last_updated = str(datetime.datetime.now())
        if IdTestament == None :
            qry = "UPDATE `testament_manager`.`request` SET Status = '" + Status + "', Comments = '" + Comments + "', DateLastModification = '" + date_last_updated + "' WHERE IdRequest='" + IdRequest + "'"
        else :
            qry = "UPDATE `testament_manager`.`request` SET Status = '" + Status + "', Comments = '" + Comments + "', IdTestament = '" + IdTestament + "', DateLastModification = '" + date_last_updated + "' WHERE IdRequest='" + IdRequest + "'"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result
    
    @staticmethod
    def updateTestament_Testator(IdTestator) :
        date_last_updated = str(datetime.datetime.now())
        qry = "UPDATE `testament_manager`.`metadataTestament` AS T1 INNER JOIN `testament_manager`.`user` AS T2 ON T1.IdTestator = T2.idnumber SET T1.Status = 'RELEASED', T1.DateLastModification = '" + date_last_updated + "', T2.Status = 'DEATH CONFIRMED', T2.DateLastModification = '" + date_last_updated + "' WHERE T1.IdTestator='" + IdTestator + "'"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result
    
    @staticmethod
    def updateRequestStatus(IdTestament, Status) :
        date_last_updated = str(datetime.datetime.now())
        qry = "UPDATE `testament_manager`.`request` SET Status = '" + Status + "', DateLastModification = '" + date_last_updated + "' WHERE IdTestament = '" + IdTestament + "' AND Status = 'DOCUMENTS VALIDATED - APPROVED'"
        result = ConexionDB.executeQry(qry,"INSERT")
        return result

        


        

    
    




    
