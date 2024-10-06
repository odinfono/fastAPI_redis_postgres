from pydantic import BaseModel, ConfigDict

class ItemBase(BaseModel):
    name: str
    description: str

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    # Update to use ConfigDict instead of class-based Config
    model_config = ConfigDict(from_attributes=True)