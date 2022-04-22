
def CreateDataLoader(opt):
    from .custom_dataset_data_loader_test import CustomDatasetDataLoader
    data_loader = CustomDatasetDataLoader()
    print(data_loader.name())
    data_loader.initialize(opt)
    return data_loader
