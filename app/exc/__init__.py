class InvalidImageError(Exception):
    def __init__(self):
        self.message = {'message': 'Invalid image format. Please send a png/jpg/jpeg file.'}
    
        super().__init__(self.message)
