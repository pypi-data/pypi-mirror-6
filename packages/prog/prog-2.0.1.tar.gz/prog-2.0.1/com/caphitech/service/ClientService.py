from com.caphitech.dao.ClientDAO import ClientDAO
import pdb

class ClientService:
    
    def __init__(self):
        pass
    
    def add(self, name):
        pdb.set_trace()
	clientDAO = ClientDAO()
        nameDAO = clientDAO.add(name)
        clientService = nameDAO + ", " + name + "Service2" 
	return clientService
 
