class CommentError(Exception):
    def __init__(self):
        self.message = {'message': 'Comment must have at least one character.'}