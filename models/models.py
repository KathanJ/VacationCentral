from pydantic import (BaseModel,
                    Field,
                    EmailStr,
                    PastDate,
                    AwareDatetime,
                    FileUrl,
                    FilePath,
                    HttpUrl,
                    GetCoreSchemaHandler,
                    GetJsonSchemaHandler)
from typing import Annotated, ForwardRef, Any, Optional
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from enum import Enum
from bson import ObjectId

#Forward References
# UserRef = ForwardRef('User')
UserIdRef = ForwardRef('UserId')
# UserInDBRef = ForwardRef('UserInDB')
UserInGroupRef = ForwardRef('UserInGroup')
UserInThreadRef = ForwardRef('UserInThread')
# ContactNoRef = ForwardRef('ContactNo')
# TagRef = ForwardRef('Tag')
# DiaryRef = ForwardRef('Diary')
DiaryIdRef = ForwardRef('DiaryId')
# ThreadRef = ForwardRef('Thread')
ThreadIdRef = ForwardRef('ThreadId')
# PostRef = ForwardRef('Post')
PostIdRef = ForwardRef('PostId')
# CommentRef = ForwardRef('Comment')
CommentIdRef = ForwardRef('CommentId')
# GroupRef = ForwardRef('Group')
GroupIdRef = ForwardRef('GroupId')
# AddressRef = ForwardRef('Address')
# PaymentInfoRef = ForwardRef('PaymentInfo')
# NotificationRef = ForwardRef('Notification')
NotificationIdRef = ForwardRef('NotificationId')

#Enums
class Sex(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"
    unspecified = None

class Payment_Method(str, Enum):
    cards = "Card"
    upi = "UPI"
    wallet = "Wallet"

# class ObjectType(Enum):
#     user = UserRef
#     userindb = UserInDBRef
#     useringroup = UserInGroupRef
#     userinthread = UserInThreadRef
#     contactno = ContactNoRef
#     tag = TagRef
#     diary = DiaryRef
#     thread = ThreadRef
#     post = PostRef
#     comment = CommentRef
#     group = GroupRef
#     address = AddressRef
#     paymentinfo = PaymentInfoRef
#     notification = NotificationRef

#BSON ObjectId Custom Validator
class ObjectIdPydanticAnnotation:
    @classmethod
    def validate_object_id(cls, v: Any, handler) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        s = handler(v)
        if ObjectId.is_valid(s):
            return ObjectId(s)
        else:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        assert source_type is Optional[ObjectId]
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_wrap_validator_function(
                    cls.validate_object_id,
                    core_schema.str_schema(),
                    serialization=core_schema.to_string_ser_schema(),
                ),
            ]
        )
        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    # Check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(Optional[ObjectId]),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.to_string_ser_schema()
        )
    #    return core_schema.no_info_wrap_validator_function(
    #            cls.validate_object_id, 
    #            core_schema.str_schema(), 
    #            serialization=core_schema.to_string_ser_schema(),
    #    )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        _core_schema = cls.__get_pydantic_core_schema__(Optional[ObjectId], GetCoreSchemaHandler())
        return handler(core_schema.str_schema())

#Pydantic Models
# class ObjectRef(BaseModel):
#     id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
#     type: str

#     @field_validator('type')
#     @classmethod
#     def check_type(cls, typ: ObjectType, info: ValidationInfo) -> ObjectType:
#         type_context = info.context


#         return typ
# print(ObjectRef(id=ObjectId('64b7abdecf2160b649ab6085'), type=ObjectType.post))
# print(ObjectRef(id=ObjectId('64b7abdecf2160b649ab6085'), type=ObjectType.post).model_dump_json())
# print(ObjectRef(id=ObjectId(), type=ObjectType.post))
# print(ObjectRef.model_json_schema())

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username: str | None = None

class ContactNo(BaseModel):
    country_code: str | None = Field(default=None, pattern="^(\\+91)|(0?)$")
    contact_no: str | None = Field(default=None, pattern="^[6-9][0-9]{9}$")

class Tag(BaseModel):
    tag_name: str
    tag_url: HttpUrl

class DiaryId(BaseModel):
    diary_id: Annotated[Optional[ObjectId], ObjectIdPydanticAnnotation] = None

class Diary(DiaryId):
    # diary_id: str
    author: UserIdRef # type: ignore
    title: str
    description: str
    location: str
    body: str
    images: list[FileUrl | FilePath] | None = None
    tags: list[Tag] | None = None
    category: str | None = None
    likes: list[UserIdRef] | None = None # type: ignore
    dislikes: list[UserIdRef] | None = None # type: ignore
    comments: list[CommentIdRef] | None = None # type: ignore
    posted_at: AwareDatetime | None = None

# class DiaryPDF(Diary):
#     diary_pdf_file: FileUrl | FilePath

class ThreadId(BaseModel):
    thread_id: Annotated[Optional[ObjectId], ObjectIdPydanticAnnotation] = None

class Thread(ThreadId):
    # thread_id: str
    owner: UserInThreadRef # type: ignore
    moderators: list[UserInThreadRef] # type: ignore
    posts: list[PostIdRef] | None = None # type: ignore
    followers: list[UserIdRef] | None = None # type: ignore
    header_image: FileUrl | FilePath | None = None
    thread_logo: FileUrl | FilePath | None = None
    created_at: AwareDatetime | None = None

class PostId(BaseModel):
    post_id: Annotated[Optional[ObjectId], ObjectIdPydanticAnnotation] = None

class Post(PostId):
    # post_id: str
    author: UserIdRef # type: ignore
    title: str
    description: str
    source_location: str
    destination_location: str
    body: str
    images: list[FileUrl | FilePath] | None = None
    tags: list[Tag] | None = None
    category: str | None = None
    thread: ThreadIdRef # type: ignore
    likes: list[UserIdRef] | None = None # type: ignore
    dislikes: list[UserIdRef] | None = None # type: ignore
    comments: list[CommentIdRef] | None = None # type: ignore
    posted_at: AwareDatetime | None = None

class CommentId(BaseModel):
    comment_id: Annotated[Optional[ObjectId], ObjectIdPydanticAnnotation] = None

class Comment(CommentId):
    # comment_id: str
    post: PostIdRef # type: ignore
    author: UserIdRef # type: ignore
    body: str
    image: FileUrl | FilePath | None = None
    tags: list[Tag] | None = None
    likes: list[UserIdRef] | None = None # type: ignore
    dislikes: list[UserIdRef] | None = None # type: ignore
    # replies: list['Comment'] | None = None
    replies: list[CommentIdRef] | None = None # type: ignore
    posted_at: AwareDatetime | None = None

class GroupId(BaseModel):
    group_id: Annotated[Optional[ObjectId], ObjectIdPydanticAnnotation] = None

class Group(GroupId):
    # group_id: str
    name: str
    description: str
    owner: UserIdRef # type: ignore
    members: list[UserInGroupRef] # type: ignore
    group_pic: FileUrl | FilePath | None = None
    tags: list[Tag] | None = None
    messages: list[CommentIdRef] | None = None # type: ignore
    created_at: AwareDatetime | None = None

class Address(BaseModel):
    user_first_name: str
    user_last_name: str
    address_line_1: str
    address_line_2: str | None = None
    city: str
    state: str
    country: str
    pincode: str = Field(pattern="^[1-9]{1}[0-9]{2}\\s{0, 1}[0-9]{3}$")

class PaymentInfo(BaseModel):
    # user: UserIdRef # type: ignore
    payment_method: Payment_Method
    billing_address: str
    shipping_address: str

class NotificationId(BaseModel):
    notification_id: Annotated[Optional[ObjectId], ObjectIdPydanticAnnotation] = None

class Notification(NotificationId):
    # notification_id: str
    user: UserIdRef # type: ignore
    title: str
    body: str
    reference: HttpUrl

class UserId(BaseModel):
    user_id: Annotated[Optional[ObjectId], ObjectIdPydanticAnnotation] = None

class User(UserId):
    # user_id: str
    username: str
    email: EmailStr
    full_name: str
    contact_no: ContactNo
    dob: PastDate
    current_location: str
    addresses: list[Address]
    sex: Sex
    aadhar_card: FileUrl | FilePath
    diaries: list[DiaryIdRef] | None = None # type: ignore
    posts: list[PostIdRef] | None = None # type: ignore
    comments: list[CommentIdRef] | None = None # type: ignore
    liked_posts: list[PostIdRef] | None = None # type: ignore
    liked_comments: list[CommentIdRef] | None = None # type: ignore
    # followers: list['User'] | None = None
    followers: list[UserIdRef] | None = None # type: ignore
    followed_threads: list[ThreadIdRef] | None = None # type: ignore
    notifications: list[NotificationIdRef] | None = None # type: ignore
    groups: list[GroupIdRef] | None = None # type: ignore
    points: int | None = None
    payment_info: list[PaymentInfo] | None = None
    banned: bool = False
    created_at: AwareDatetime | None = None

class UnsecuredUser(User):
    # password: str = Field(pattern="^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,16}$")
    password: str = Field(min_length=8, max_length=16)

class SecureUser(User):
    hashed_password: str

class UserInGroup(User):
    group_role: str

class UserInThread(User):
    thread_role: str