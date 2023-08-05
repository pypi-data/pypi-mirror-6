import document
import sys
import requests
import json
import pickle
import inspect
import urllib2, urllib
import types
import re

BASE_URI = "http://api.yhathq.com/"


class API(object):
    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.headers = {'Content-Type': 'application/json'}

    def get(self, endpoint, params):
        try:
            url = self.base_uri + endpoint + "?" + urllib.urlencode(params)
            req = urllib2.Request(url)
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req)
            rsp = response.read()
            return json.loads(rsp)
        except Exception, e:
            raise e
    
    def post(self, endpoint, params, data):
        try:
            url = self.base_uri + endpoint + "?" + urllib.urlencode(params)
            req = urllib2.Request(url)
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req, json.dumps(data))
            rsp = response.read()
            return json.loads(rsp)
        except Exception, e:
            raise e

class Yhat(API):
    """
    Welecome to Yhat!
    ---------------------------------------------------------------------------
    There are 2 required functions which you must implement:
    - transform
    - predict

    Transform takes the raw data that's going to be sent to your yhat API and
    converts it into the format required to be run through your model. In the
    example below (see SMS example), our transform function does the following:
        1) converts the raw_data into a list. This is because our tfidf
           vectorizer takes a list of raw text as its only argument
        2) uses the tfidf vectorizer to transform the data and returns the
           results
    ---------------------------------------------------------------------------
    Predict executes your predictive model, formats the data into response, and
    returns it. In the example below, our predict doees the following:
        1) calls the predict_proba function of our naive bayes classifier (clf)
        2) creates a variable called first_prediction which is the first item in
           the list of probabilities that is returend by predict_proba
        3) returns a dictionary witt the predicted probabilities
    
    ---------------------------------------------------------------------------

    By inheriting from BaseModel, your model recieves additional functionality

    Importing modules:

    By default, numpy and pandas will be automatically imported as np and pd.

    If you need to import libraries you may do so from within the transform or
    predict functions. Currently we only support base Python libraries, sklearn,
    numpy, and pandas

        def transform(self, raw_data):
            import string
            punc_count = len([ch for ch in raw_data if ch in string.punctuation])
            ...
    ---------------------------------------------------------------------------
    """

    def __init__(self, username, apikey, uri=BASE_URI):
        self.username = username
        self.apikey = apikey
        self.base_uri = uri
        self.headers = {'Content-Type': 'application/json'}
        self.q = {"username": self.username, "apikey": apikey}

    def _check_obj_size(self, obj):
        if self.base_uri!=BASE_URI:
            # not deploying to the cloud so models can be as big as you want
            pass
        elif sys.getsizeof(obj) > 52428800:
            raise Exception("Sorry, your file is too big for a free account.")

    def show_models(self):
        """
        Lists the models you've deployed.
        """
        return self.get("showmodels", self.q)

    def raw_predict(self, model, version, data):
        """
        Runs a prediction for the model specified and returns the same
        prediction you would see from the REST API
        """
        data = {"data": data}
        q = self.q
        q['model'] = model
        q['version'] = version
        if self.base_uri!=BASE_URI:
            return self.post('models/%s/' % model, q, data)
        else:
             return self.post('predict', q, data)

    def predict(self, model, version, data):
        """
        Runs a prediction for the model specified and returns only the
        prediction.
        """
        rawResponse = self.raw_predict(model, version,  data)
        if 'prediction' in rawResponse:
            return rawResponse['prediction']
        else:
            return rawResponse

    def _extract_source(self, modelname, pml, className):

        filesource = "#<start user imports>\n"
        import_source = inspect.getsource(pml.require)
        imports = [line.strip() for line in import_source.split('\n') if "import" in line]
        imports = [i for i in imports if i.startswith("#")==False]
        filesource += "\n".join(imports) + "\n"
        filesource += "#<end user imports>\n\n"

        filesource += "#<start user functions>\n"
        if hasattr(pml, "udfs"):
            for udf in pml.udfs:
                if isinstance(udf, types.FunctionType):
                    source = inspect.getsource(udf).split("\n")
                    padding = re.search('[ ]+', source[0]).group(0)
                    for line in source:
                        filesource += line[len(padding):] + "\n"
                    filesource += "\n"
        filesource += "#<end user functions>\n"

        filesource += "\n"
        filesource += "class %s(BaseModel):" % className + "\n"
        filesource += inspect.getsource(pml.transform)+ "\n"
        filesource += inspect.getsource(pml.predict)

        return filesource

    def document(self, model, version, example_data):
        """
        Automatically documents your model and creates a webpage where you 
        can test your model.

        model - the name of your model
        version - the version of your model
        example_data - a pandas DataFrame with required columns to execute your
                    model
        """
        q = self.q
        q['model'] = model
        q['version'] = version
        docs = document.document_data(example_data)
        return self.post('document', q, {"docs": docs})

    def deploy(self, modelname, pml):
        """
        Deploys your model to the Yhat servers.

        Note: this will eventually replace Yhat.upload
        """
        return self.upload(modelname, pml)

    def upload(self, modelname, pml):
        """
        Uploads your model to the Yhat servers.
        """
        print "uploading...",
        try:
            className = pml.__class__.__name__
            filesource = self._extract_source(modelname, pml, className)
        except Exception, e:
            print "Could not extract code. Either re-run script."
        userFiles = vars(pml)
        pickledUserFiles = {}
        for f, uf in userFiles.iteritems():
            if f=="udfs":
                continue
            pickledUserFiles[f] = pickle.dumps(uf)
            self._check_obj_size(pickledUserFiles[f])
        payload = {
            "modelname": modelname,
            "modelfiles": pickledUserFiles,
            "code": filesource,
            "className": className,
            "reqs": getattr(pml, "requirements", "")
        }
        rsp = self.post("model", self.q, payload)
        print "done!"
        return rsp

