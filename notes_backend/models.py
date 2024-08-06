from notes_backend.core.NotesBaseModel import NotesBaseModel


class StatusResponse(NotesBaseModel):
    status: bool = True
