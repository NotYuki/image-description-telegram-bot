import cloudmersive_image_api_client
from cloudmersive_image_api_client.models.image_description_response import ImageDescriptionResponse
from cloudmersive_image_api_client.rest import ApiException

CLOUDMERSIVE_API_KEY_FILE = '../src/cloudmersive_api_key'


class ImageProcessor:
    """
    Class uses Cloudmersive Image Recognition ML API.
    For more details look for specific method docstring.
    API Doc: https://api.cloudmersive.com/docs/image.asp
    """

    def __init__(self):
        with open(CLOUDMERSIVE_API_KEY_FILE) as kf:
            api_key = kf.read().strip()

        # Configure API key authorization: Apikey
        configuration = cloudmersive_image_api_client.Configuration()
        configuration.api_key['Apikey'] = api_key

        # Create an instance of the API class
        self.api_instance = cloudmersive_image_api_client.RecognizeApi(
            cloudmersive_image_api_client.ApiClient(configuration))

    def recognize_image(self, image_file: str) -> ImageDescriptionResponse:
        """
        Generate an English language text description of the image as a sentence.
        :param image_file: Path to image file to perform the operation on. Common file formats such as PNG, JPEG are supported.
        :return: Image description in English
        """
        try:
            # Describe an image in natural language
            return self.api_instance.recognize_describe(image_file)
        except ApiException as e:
            print("Exception when calling RecognizeApi->recognize_describe: %s\n" % e)
