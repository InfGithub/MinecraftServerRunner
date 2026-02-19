from typing import Any, Literal, Callable, Unpack
from util import Config, Color, colorize, ColorArgs

type InputSetAllowedType = Literal["int", "str", "bool"]

# ----------------------------------------------------------------

class Page:
	def __init__(self, base_color: Color | list[Color] = "", error_color: Color = "red"):
		if isinstance(base_color, str):
			self.base_colors = [base_color] if base_color else list()
		else:
			self.base_colors = base_color
		self.error_color = error_color

	def print(self, text: str, is_error: bool = False, *colors: Color, **kwargs):
			print(colorize(
				text, *colors, *self.base_colors, self.error_color if is_error else ""
				), **kwargs
			)

	def do(self):
		raise NotImplementedError("Unknown Action Function 'do'")

	def line(self, text: str = "-" * 64, **kwargs):
		print(colorize(text, *self.base_colors), **kwargs)

	def input(self, prompt: str) -> str:
		self.print(prompt, end="")
		return input()

# ----------------------------------------------------------------

class Choose(Page):
	def __init__(
		self,
		text: list[str],
		data: list[Page | Any],
		description: str,
		prompt: str = None,
		callback: bool = True,
		config: Config = None,
		config_key: str = None,
		exit_call_function: Callable = None,
		end_line: bool = True,
		value_mapping: dict[int, Any] = None,
		current_value_key: str = None,
		display_current_value: bool = True,
		**kwargs: Unpack[ColorArgs]
	):
		super().__init__(**kwargs)
		self.text: list[str] = text
		self.data: list[Page | Any] = data
		self.description: str = description
		self.prompt: str = prompt
		self.callback: bool = callback
		self.config: Config = config
		self.config_key: str = config_key
		self.index_max: int = len(self.data) - 1
		self.exit_call_function: Callable = exit_call_function
		self.end_line: bool = end_line
		self.value_mapping: dict[int, Any] = value_mapping
		self.current_value_key: str = current_value_key

		if self.config and self.current_value_key is None and display_current_value:
			self.current_value_key: str = self.config_key

	def do(self):
		self.print(f"{self.description}")
		self.line()

		tips: list[str] = list()
		if self.prompt:
			tips.append(f"提示：{self.prompt}")
		if self.callback:
			tips.append(f"按下Ctrl+C退出此页面。")
		if not self.current_value_key is None:
			tips.append(f"当前值：{self.config[self.current_value_key]}")

		if tips:
			for text in tips:
				self.print(text)
			self.line()

		for index, item in enumerate(self.text):
			self.print(f"[{index}] {item}")

		self.line()

		while True:
			try:
				result: str = self.input("输入：")
			except KeyboardInterrupt as err:
				print()

				if self.callback:
					if self.exit_call_function:
						self.exit_call_function()
					self.line()
					self.print(f"已退出此页面。")
					if self.end_line:
						self.line()
					return
				else:
					self.line()
					self.print(f"异常：捕获{err}。", is_error=True)
					self.line()
					continue

			if not result:
				self.print(f"异常：输入为空。", is_error=True)
				self.line()
				continue

			if not result.isdigit():
				self.print(
					f"异常：数据类型错误，应为{int}类型，取值范围：0 - {self.index_max}。",
					is_error=True
				)
				self.line()
				continue

			value: int = int(result)

			if value > self.index_max:
				self.print(f"异常：索引溢出，取值范围：0 - {self.index_max}。", is_error=True)
				self.line()
				continue

			var: Page | Any = self.data[value]

			if isinstance(var, Page):
				self.line()
				var.do()
			else:
				if self.value_mapping:
					if value in self.value_mapping: # 提供映射表以映射值
						var = self.value_mapping[value]
				self.config.set(self.config_key, var)
				if self.end_line:
					self.line()
				self.print(f"修改成功，已退出此页面。")
				self.line()
				return

# ----------------------------------------------------------------

class InputSet(Page):
	def __init__(
		self,
		description: str,
		config: Config,
		config_key: str,
		data_type: InputSetAllowedType,
		prompt: str = None,
		callback: bool = True,
		exit_call_function: Callable = None,
		complete_call_function: Callable = None,
		current_value_key: str = None,
		display_current_value: bool = True,
		default: str = None,
		**kwargs: Unpack[ColorArgs]
	):
		super().__init__(**kwargs)
		self.description: str = description
		self.prompt: str = prompt
		self.callback: bool = callback
		self.config: Config = config
		self.config_key: str = config_key
		self.data_type: InputSetAllowedType = data_type
		self.exit_call_function: Callable = exit_call_function
		self.complete_call_function: Callable = complete_call_function
		self.current_value_key: str = current_value_key
		self.default: str = default

		if self.config and self.current_value_key is None and display_current_value:
			self.current_value_key: str = self.config_key

	def do(self):
		self.print(f"{self.description}")
		self.line()

		tips: list[str] = list()
		if self.prompt:
			tips.append(f"提示：{self.prompt}")
		if self.callback:
			tips.append(f"按下Ctrl+C退出此页面。")
		if self.data_type == "bool":
			tips.append(f"输入y/n来指定布尔值。")
		if not self.current_value_key is None:
			tips.append(f"当前值：{self.config[self.current_value_key]}")
		if not self.default is None:
			tips.append(f"输入为空时使用默认值：{self.default}。")

		if tips:
			for text in tips:
				self.print(text)
			self.line()

		while True:
			try:
				result: str = self.input("输入：")
			except KeyboardInterrupt as err:
				print()

				if self.callback:
					if self.exit_call_function:
						self.exit_call_function()
					self.print(f"已退出此页面。")
					return
				else:
					self.line()
					self.print(f"异常：捕获{err}。", is_error=True)
					self.line()
					continue

			if not result:
				if self.default is None:
					self.print(f"异常：输入为空。", is_error=True)
					self.line()
					continue
				else:
					result: str = self.default
					self.line()

			if self.data_type == "int":
				if not result.lstrip("-").isdigit():
					self.print(f"异常：数据类型错误，应为{int}类型。", is_error=True)
					self.line()
					continue

				value: int = int(result)

			elif self.data_type == "str":
				value: str = result

			elif self.data_type == "bool":
				char: str = result[0].lower()
				if not char in {"y", "n"}:
					self.print(f"异常：数据内容错误，应为y/n。", is_error=True)
					self.line()
					continue

				is_yeah: bool = char == "y"
				value: bool = is_yeah

			self.config.set(self.config_key, value)
			self.print(f"修改成功，已退出此页面。")
			self.line()

			if self.complete_call_function:
				self.complete_call_function()
			return

class InfoList(Page):
	def __init__(
		self,
		texts: list[str] = None,
		description: str = None,
		call_function: Callable[[], list[str]] = None,
		complete_call_function: Callable = None,
		enable_exit_prompt: bool = False,
		**kwargs: Unpack[ColorArgs]
	):
		super().__init__(**kwargs)
		if not texts:
			texts: list[str] = list()
		self.texts: list[str] = texts
		self.description: str = description
		self.call_function: Callable[[], list[str]] = call_function
		self.complete_call_function: Callable = complete_call_function
		if enable_exit_prompt:
			self.texts.insert(0, "按下Ctrl+C以退出，将不会进行操作。")

	def do(self):
		if self.description:
			self.print(self.description)
			self.line()

		if self.texts:
			for item in self.texts:
				self.print(item)
			self.line()

		if self.call_function:
			result: list[str] = self.call_function()

			if result:
				for item in result:
					self.print(item)
				self.line()
		try:
			self.input("按下任意键以继续。")
			if self.complete_call_function:
				self.complete_call_function()
		except KeyboardInterrupt as err:
			print()
		self.line()