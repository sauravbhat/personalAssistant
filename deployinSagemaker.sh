

echo "deploying "


pip install shortuuid
pip install yaspin wheel requests
pip install --upgrade setuptools
pip install sagemaker --upgrade

python deployinSagemakerHF.py
