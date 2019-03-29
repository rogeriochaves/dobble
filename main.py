from timeit import default_timer as timer
print("Loading models...")
start = timer()

import sys
import pickle
from functools import partial
from dobble.utilities import Config, current_ram
import dobble.model as model
import dobble.server as server

config_output_filename = 'model_vgg_config.pickle'
with open(config_output_filename, 'rb') as f_in:
    C = pickle.load(f_in)

model_rpn, model_classifier_only = model.build(C)
print("Model ready")
end = timer()
print("Done! Models loaded in", "{:.1f}".format(end - start),
      "seconds. Using", current_ram(), "of RAM")

predict = partial(model.predict, C, model_rpn, model_classifier_only)
if "--server" in sys.argv:
    server.start(predict)
else:
    result = predict('custom_pics/IMG_3430.jpg')
    print(result)
