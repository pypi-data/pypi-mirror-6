import xbob.thesis.elshafey2014

# define a queue with parameters to train ISV
grid = xbob.thesis.elshafey2014.utils.ParaGridParameters(
  init_training_queue = {'queue' : 'q1wm', 'memfree' : '32G', 'pe_opt' : 'pe_mth 4', 'hvmem' : '8G'},
  training_queue = {'queue' : 'q1wm', 'memfree' : '32G', 'pe_opt' : 'pe_mth 4', 'hvmem' : '8G'},
  # preprocessing
  number_of_preprocessings_per_job = 1000,
  # feature extraction
  number_of_extracted_features_per_job = 1000,
  extraction_queue = 'default',
  # feature projection
  number_of_projected_features_per_job = 200,
  projection_queue = 'default',
  # model enrollment
  number_of_enrolled_models_per_job = 20,
  enrollment_queue = 'default',
  # scoring
  number_of_models_per_scoring_job = 20,
  scoring_queue = 'default'
)
# add special queue parameters for the ISV training
grid.isv_training_queue = grid.queue('default')

