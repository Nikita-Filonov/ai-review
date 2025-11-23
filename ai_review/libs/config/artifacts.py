from pydantic import BaseModel, DirectoryPath, field_validator, Field


class ArtifactsConfig(BaseModel):
    llm_dir: DirectoryPath = Field(default=DirectoryPath("./artifacts/llm"), validate_default=True)
    vcs_dir: DirectoryPath = Field(default=DirectoryPath("./artifacts/vcs"), validate_default=True)
    llm_enabled: bool = False
    vcs_enabled: bool = False

    @field_validator('llm_dir', 'vcs_dir', mode='before')
    def validate_directories(cls, value: DirectoryPath | str) -> DirectoryPath:
        directory = DirectoryPath(value)
        directory.mkdir(parents=True, exist_ok=True)
        return directory
