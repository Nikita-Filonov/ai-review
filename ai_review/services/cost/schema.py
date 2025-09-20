from pydantic import BaseModel


class CostReportSchema(BaseModel):
    model: str
    prompt_tokens: int
    completion_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float

    @property
    def prompt_percent(self) -> float:
        return (self.input_cost / self.total_cost * 100) if self.total_cost else 0.0

    @property
    def completion_percent(self) -> float:
        return (self.output_cost / self.total_cost * 100) if self.total_cost else 0.0

    @property
    def pretty_total_line(self) -> str:
        return f"- {'Total:':<20} {'':>7}   {self.total_cost:12.6f} USD"

    @property
    def pretty_prompt_line(self) -> str:
        return (
            f"- {'Prompt tokens:':<20} {self.prompt_tokens:>7} → "
            f"{self.input_cost:12.6f} USD ({self.prompt_percent:.1f}%)"
        )

    @property
    def pretty_completion_line(self) -> str:
        return (
            f"- {'Completion tokens:':<20} {self.completion_tokens:>7} → "
            f"{self.output_cost:12.6f} USD ({self.completion_percent:.1f}%)"
        )

    def pretty(self) -> str:
        return (
            f"\n💰 Estimated Cost for `{self.model}`\n"
            f"{self.pretty_prompt_line}\n"
            f"{self.pretty_completion_line}\n"
            f"{self.pretty_total_line}\n"
        )
