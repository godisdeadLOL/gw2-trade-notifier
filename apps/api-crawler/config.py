from pydantic import BaseModel, Field
import dotenv


class Config(BaseModel):
    app_name: str = "api-crawler"
    redis_url: str = Field(alias="REDIS_URL")
    mongo_url: str = Field(alias="MONGO_URL")


dotenv.load_dotenv()
config = Config.model_validate(dotenv.dotenv_values(".env"))
