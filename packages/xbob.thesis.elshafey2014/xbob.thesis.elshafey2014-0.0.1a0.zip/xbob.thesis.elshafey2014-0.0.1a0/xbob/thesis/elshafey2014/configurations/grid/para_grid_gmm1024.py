import xbob.thesis.elshafey2014

# define a queue with parameters to train ISV
grid = xbob.thesis.elshafey2014.utils.ParaGridParameters(
  init_training_queue = '64G',
  training_queue = '8G-io-big',
  # preprocessing
  number_of_preprocessings_per_job = 1000,
  # feature extraction
  number_of_extracted_features_per_job = 1000,
  extraction_queue = '8G-io-big',
  # feature projection
  number_of_projected_features_per_job = 200,
  projection_queue = '8G-io-big',
  # model enrollment
  number_of_enrolled_models_per_job = 20,
  enrollment_queue = '8G-io-big',
  # scoring
  number_of_models_per_scoring_job = 20,
  scoring_queue = '8G-io-big'
)
# add special queue parameters for the ISV training
grid.isv_training_queue = grid.queue('8G-io-big')

