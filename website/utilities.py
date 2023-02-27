from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from website import app, mail
import mimetypes, json
from ast import literal_eval
from web3 import Web3, exceptions
import website.parameters as parameters
import asyncio


abiContract = ""
provider_url = parameters.urlB
w3 = Web3(Web3.HTTPProvider(provider_url))
w3.clientVersion

addressC = parameters.contractA
with open('ABI.json') as json_file:
    abiContract = json.load(json_file)
counter = w3.eth.contract(address = addressC, abi = abiContract)

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def send_email(to, subject, template, attachment = None):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )

    if attachment !=  None :
        file = open(attachment,'rb')
        print(mimetypes.guess_type(attachment)[0])
        msg.attach(filename = "Testament", 
                        content_type = mimetypes.guess_type(attachment)[0],
                        data=file.read())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(sending(msg))

async def sending(msg):
    mail.send(msg)
    
def sendTransactionBl(data):
    try :
        if w3.isConnected():
            transaction = counter.functions.update(data).buildTransaction({'chainId': int(parameters.chainId), 'gas':120000, 'nonce': w3.eth.getTransactionCount(parameters.wallerA)})
            signed_txn = w3.eth.account.signTransaction(transaction, parameters.walletK)
            txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            return txn_hash
        else:
            #app.logger.critical("ERR Blockchain Payload " + str(data))
            return "ERR: Connection to Blockchain not possible."
    except ValueError as e:
        return "ERR: Error executing transaction in the blockchain."

def getTransactionBl(txnHash):
    try :
        if w3.isConnected():
            tx = w3.eth.getTransaction(txnHash) 
            func_obj, func_params = counter.decode_function_input(tx["input"])
            return func_params
        else:
            return "ERR: Connection to Blockchain not possible."
    except exceptions.TransactionNotFound :
        return "ERR: Testament information not found it in the system."
    except:
        return "ERR: Error in the connection to the Blockchain, try later."






