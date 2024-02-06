packnames = ('stringi','lme4','tidyverse', 'afex', 'remotes') #, 'lmerTest', 'emmeans', "geepack")
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import StrVector

utils = importr("utils")
utils.chooseCRANmirror(ind=1)
utils.install_packages(StrVector(packnames))

# Install old version of ggeffects: ggpredict in newer version with same arguments reverses sg and pl
remotes = importr("remotes")
remotes.install_version("ggeffects", version = "1.3.1", repos = "http://cran.us.r-project.org")

