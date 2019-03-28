import pickle
from timeit import default_timer as timer
from dobble.utilities import Config
import dobble.model as model

config_output_filename = 'model_vgg_config.pickle'
with open(config_output_filename, 'rb') as f_in:
    C = pickle.load(f_in)


model_rpn, model_classifier_only = model.build(C)

print("Model ready")

start = timer()
result = model.predict(C, model_rpn, model_classifier_only,
                       img_path='custom_pics/IMG_3521.jpg')
print(result)
end = timer()
print("Time spent:", end - start)
