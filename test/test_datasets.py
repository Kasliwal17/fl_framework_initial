import os
import sys
import unittest
from server.src.server_lib import save_intial_model
from misc import get_config, tester
# add main directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_train_test_for_MNIST():
    '''
    This function us used to verify the MNIST dataset 
    using one clients
    '''
    class TrainerTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            config = get_config('test_datasets', 'MNIST')
            save_intial_model(config['server'])

        def test_MNIST(self):
            print("\n======================MNIST Testing======================")
            config = get_config('test_datasets', 'MNIST')
            tester(config, 1)

    return TrainerTest


def create_train_test_for_FashionMnist():
    '''
    This function us used to verify the FashionMNIST dataset 
    using one clients
    '''
    class TrainerTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            config = get_config('test_datasets', 'FashionMNIST')
            save_intial_model(config['server'])

        def test_FashionMnist(self):
            print("\n======================FashionMNIST Testing======================")
            config = get_config('test_datasets', 'FashionMNIST')
            tester(config, 1)

    return TrainerTest

def create_train_test_for_CIFAR10():
    '''
    This function us used to verify the CIFAR10 dataset 
    using one client
    '''
    class TrainerTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            config = get_config('test_datasets', 'CIFAR10')
            save_intial_model(config['server'])

        def test_CIFAR10(self):
            print("\n======================CIFAR10 Testing======================")
            config = get_config('test_datasets', 'CIFAR10')
            tester(config, 1)

    return TrainerTest


def create_train_test_for_CIFAR100():
    '''
    This function us used to verify the CIFAR100 dataset 
    using one client
    '''
    class TrainerTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            config = get_config('test_datasets', 'CIFAR100')
            save_intial_model(config['server'])

        def test_CIFAR100(self):
            print("\n======================CIFAR100 Testing======================")
            config = get_config('test_datasets', 'CIFAR100')
            tester(config, 1)

    return TrainerTest


def create_train_test_for_CUSTOM():
    '''
    This function us used to verify the CUSTOM dataset 
    using one client
    '''
    class TrainerTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            config = get_config('test_datasets', 'CUSTOM')
            save_intial_model(config['server'])

        def test_CUSTOM(self):
            print("\n=====================CUSTOM Dataset Testing======================")
            config = get_config('test_datasets', 'CUSTOM')
            tester(config, 1)

    return TrainerTest

class TestTrainer_MNIST(create_train_test_for_MNIST()):
    'Test case for MNIST dataset'

class TestTrainer_FashionMNIST(create_train_test_for_FashionMnist()):
    'Test case for FashionMNIST dataset'

class TestTrainer_CIFAR10(create_train_test_for_CIFAR10()):
    'Test case for CIFAR10 dataset'

class TestTrainer_CIFAR100(create_train_test_for_CIFAR100()):
    'Test case for CIFAR100 dataset'

class TestTrainer_CUSTOM(create_train_test_for_CUSTOM()):
    'Test case for CUSTOM dataset'

if __name__ == '__main__':

    unittest.main()
