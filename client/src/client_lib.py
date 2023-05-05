import torch
from io import BytesIO
import json
import time
import os 
from datetime import datetime
from codecarbon import EmissionsTracker, OfflineEmissionsTracker
from .net import get_net
from .net_lib import test_model, load_data, flush_memory, DEVICE
from .net_lib import train_model, train_fedavg, train_scaffold, train_mimelite, train_mime, train_feddyn
from torch.utils.data import DataLoader
from .get_data import get_data

from .ClientConnection_pb2 import  EvalResponse, TrainResponse

#create a new directory inside FL_checkpoints and store the aggragted models in each round
device = torch.device("cuda:2" if torch.cuda.is_available() else "cpu") #device id  of this should be same in net_lib device
fl_timestamp = f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"
save_dir_path = f"client_checkpoints/{fl_timestamp}"
os.makedirs(save_dir_path)

def evaluate(eval_order_message):
    model_parameters_bytes = eval_order_message.modelParameters
    model_parameters = torch.load( BytesIO(model_parameters_bytes), map_location="cpu" )

    config_dict_bytes = eval_order_message.configDict
    config_dict = json.loads( config_dict_bytes.decode("utf-8") )
    
    state_dict = model_parameters
    print("Evaluation:",config_dict)
    with open("config.json", "r") as jsonfile:
        config_dict = json.load(jsonfile)
    model = get_net(config= config_dict).to(device)
    model.load_state_dict(state_dict)
    
    _, testset = get_data(config= config_dict)
    testloader = DataLoader(testset, batch_size=config_dict['batch_size'])
    
    #_, testloader, _ = load_data(config_dict)
    
    
    eval_loss, eval_accuracy = test_model(model, testloader)

    response_dict = {"eval_loss": eval_loss, "eval_accuracy": eval_accuracy}
    response_dict_bytes = json.dumps(response_dict).encode("utf-8")
    eval_response_message = EvalResponse(responseDict = response_dict_bytes)
    return eval_response_message


def train(train_order_message):
    data_bytes = train_order_message.modelParameters
    data = torch.load( BytesIO(data_bytes), map_location="cpu" )
    model_parameters, control_variate, control_variate2 = data['model_parameters'], data['control_variate'], data['control_variate2']
    
    config_dict_bytes = train_order_message.configDict
    config_dict = json.loads( config_dict_bytes.decode("utf-8") )
    carbon_tracker = config_dict["carbon-tracker"]

    model = get_net(config= config_dict)
    model.load_state_dict(model_parameters)
    model = model.to(device)
    epochs = config_dict["epochs"]
    if config_dict["timeout"]:
        deadline = time.time() + config_dict["timeout"]
    else:
        deadline = None
    
    #Run code carbon if the carbon-tracker flag is True
    if (carbon_tracker==1):
	    tracker = OfflineEmissionsTracker(country_iso_code="IND", output_dir = save_dir_path)
	    tracker.start()
            
    trainloader, testloader, _ = load_data(config_dict)
    print("Training started")
    if (config_dict['algorithm'] == 'mimelite'):
        model, control_variate = train_mimelite(model, control_variate, trainloader, epochs, deadline)
    elif (config_dict['algorithm'] == 'scaffold'):
        model, control_variate = train_scaffold(model, control_variate, trainloader, epochs, deadline)
    elif (config_dict['algorithm'] == 'mime'):
        model, control_variate = train_mime(model, control_variate, control_variate2, trainloader, epochs, deadline)
    elif (config_dict['algorithm'] == 'fedavg'):
        model = train_fedavg(model, trainloader, epochs, deadline)
    elif (config_dict['algorithm'] == 'feddyn'):
        model = train_feddyn(model, trainloader, epochs, deadline)
    else:
        model = train_model(model, trainloader, epochs, deadline)

    if (carbon_tracker==1):
	    emissions: float = tracker.stop()
	    print(f"Emissions: {emissions} kg")

    myJSON = json.dumps(config_dict)
    json_path = save_dir_path + "/config.json"
    with open(json_path, "w") as jsonfile:
        jsonfile.write(myJSON)
    json_path = "config.json"
    with open(json_path, "w") as jsonfile:
        jsonfile.write(myJSON)
    
    trained_model_parameters = model.state_dict()
    #Create a dictionary where model_parameters and control_variate are stored which needs to be sent to the server
    data_to_send = {}
    data_to_send['model_parameters'] = trained_model_parameters
    data_to_send['control_variate'] = control_variate #If there is no control_variate, this will become None
    buffer = BytesIO()
    torch.save(data_to_send, buffer)
    buffer.seek(0)
    data_to_send_bytes = buffer.read()   

    print("Evaluation")
    train_loss, train_accuracy = test_model(model, testloader)
    response_dict = {"train_loss": train_loss, "train_accuracy": train_accuracy}
    response_dict_bytes = json.dumps(response_dict).encode("utf-8")

    train_response_message = TrainResponse(
        modelParameters = data_to_send_bytes, 
        responseDict = response_dict_bytes)

    save_model_state(model)
    return train_response_message

#replace current model with the model provided
def set_parameters(set_parameters_order_message):
    model_parameters_bytes = set_parameters_order_message.modelParameters
    model_parameters = torch.load( BytesIO(model_parameters_bytes), map_location="cpu" )
    with open("config.json", "r") as jsonfile:
        config_dict = json.load(jsonfile)
    model = get_net(config= config_dict).to(device)
    model.load_state_dict(model_parameters)
    save_model_state(model)

#save the current model to model_checkpoints
def save_model_state(model):
    file_num = len(os.listdir(f"{save_dir_path}"))
    filepath = f"{save_dir_path}/model_{file_num}.pt"
    state_dict = model.state_dict()
    torch.save(state_dict, filepath)
