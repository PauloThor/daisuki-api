class InvalidImageError(Exception):
    def __init__(self):
        self.message = {'message': 'Invalid image format. Please send a png/jpg/jpeg file.'}
    
        super().__init__(self.message)


class DuplicatedDataError(Exception):
    def __init__(self, data) -> None:
        self.message = {'message': f'{data} already exists.'}


class PageNotFoundError(Exception):
    def __init__(self, data) -> None:
        self.message = {'message': f'Page {data} not found.'}


class DataNotFound(Exception):
    def __init__(self, data) -> None:
        self.message = {'message': f'{data} not found.'}
