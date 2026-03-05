from pydantic import BaseModel, EmailStr, field_validator


class CreateUserRequest(BaseModel):
	username: str
	password: str
	email: EmailStr  # Automatically validates email format

	# TODO uncomment validator when done testing
	@field_validator('username')
	def validate_username(cls, v):
		if not all(32 <= ord(c) <= 126 for c in v):  # visible ASCII
			raise ValueError("Username must contain only visible ASCII characters")
		if any(c in v for c in ['*', '+', '~', '`', '<', '>', '@']):
			raise ValueError("Username contains forbidden characters: *, +, ~, `, <, >, @")
		# if len(v) < 5:
		# 	raise ValueError("Username must be at least 5 characters long")
		return v

	# TODO uncomment validator when done testing
	@field_validator('password')
	def validate_password(cls, v):
		if len(v) < 5:
			raise ValueError("Password must be at least 5 characters long")
		# if not all(32 <= ord(c) <= 126 for c in v):  # visible ASCII
		# 	raise ValueError("Password must contain only visible ASCII characters")
		# if not re.search(r'[A-Z]', v):
		# 	raise ValueError("Password must include at least one uppercase letter")
		# if not re.search(r'[a-z]', v):
		# 	raise ValueError("Password must include at least one lowercase letter")
		# if not re.search(r'\d', v):
		# 	raise ValueError("Password must include at least one number")
		return v


class Token(BaseModel):
	access_token: str
	token_type: str
