import time
from lobe import ImageModel
from lobe.Signature import Signature
import lobe
from app_settings import AppSettings

_app_settings = AppSettings()
#model:ImageModel = ImageModel.load('~/code/bee/BeeCam/tf_models')
#sig: Signature = Signature('/home/pi/code/bee/BeeCam/tf_models_lite')
#model: ImageModel = ImageModel.load_from_signature(sig)
#model: ImageModel = ImageModel.load('./tf_models_lite')

sig:Signature = Signature('./tf_models_lite/signature.json')
model: ImageModel = ImageModel.load_from_signature(sig)
#test_model: ImageModel = ImageModel.load_from_signature(Signature('./tf_models_lite/sig.json'))
#model_not_a_bee: ImageModel = ImageModel.load()

'''
The TFClassify class (Tensor Flow Classifier), takes a TensorFlow model and allows you
to pass multiple images to it via the addImage() or addImages() methods. It then
returns the predicted classification of the images as a DICT array
{
    'image': '<image_path_sent_to_classifier>',
    'prediction': 'output_prediction_from_TensorFlow'>
}
'''
class TFClassify:
    def __init__(self):
        self.images = []
        self.results = []
    #Add a single image to the classifier
    def addImage(self, imagePath) -> int:
        self.images.append(imagePath)
        return len(self.images)
    #Add an array of images to the classifier
    def addImages(self, imagePaths:[]) -> int:
        self.images = imagePaths
        return len(self.images)

    #Clears the image array
    def reset(self):
        self.images, self.results = [], []

    def create_json_result(self, prediction, image_path, confidence="X"):
        calc_val = lambda prediction, item: 1 if prediction == item else 0
        valid_labels = _app_settings.get_TFLabels()
        #IoT Central maps these keys to specific values in the JSON Response. Need to match
        dicList = {k: v for (k, v) in zip(valid_labels, valid_labels)}
        result = {
            "Confidence": confidence,
            "Prediction": prediction,
            "Image": image_path
        }
        for key, value in dicList.items():
            if key == prediction:
                result[value] = 1
            else:
                result[value] = 0
        return result


    '''For each image in the images collection, process it, and then return
        an array of results. Each item in the array is a dictionary:
        {image:<image_path>, prediction:<prediction_from_tensorflow>}
    '''
    def doClassify(self) -> []:
        for item in self.images:
            res = model.predict_from_file(item)
            predict, confidence = res.labels[0]
            result = self.create_json_result(predict, item, confidence)
            self.results.append(result)
        return self.results



if __name__ == '__main__':
    classifier = TFClassify()
    classifier.reset()
    classifier.addImage('tf_models/1.jpeg')
    classifier.addImage('tf_models/2.jpeg')
    results = classifier.doClassify()
    for r in results:
        print(r)
