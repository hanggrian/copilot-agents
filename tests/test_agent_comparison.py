from unittest import main, TestCase

from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.metrics.g_eval.g_eval import SingleTurnParams
from deepeval.test_case import LLMTestCase

from .llms import OPENAI_GENERATOR_MODEL, OPENAI_REVIEWER_MODEL, openai_llm


def _load_prompt(path: str) -> str:
    with open(path, encoding='UTF-8') as fh:
        text = fh.read()
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            text = parts[2]
    return text.strip()


def _load_full(path: str) -> str:
    with open(path, encoding='UTF-8') as fh:
        return fh.read().strip()


def _query(prompt: str, question: str) -> str:
    return openai_llm \
        .chat \
        .completions \
        .create(
            model=OPENAI_GENERATOR_MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': prompt,
                },
                {
                    'role': 'user',
                    'content':
                        'Answer the following directly from your knowledge. Do not describe ' +
                        'your research process, search steps, or methodology — just provide the ' +
                        f'answer.\n\n{question}',
                },
            ],
            temperature=0.0,
            max_tokens=2048,
        ).choices[0] \
            .message \
            .content or ''


EXPLAINER_PROMPT = _load_prompt('Explainer.agent.md')
ASK_PROMPT = _load_prompt('template/Ask.agent.md')
EXPLAINER_FULL = _load_full('Explainer.agent.md')
ASK_FULL = _load_full('template/Ask.agent.md')
QUESTIONS = [
    'How does Flask handle request routing internally? Explain the WSGI application flow.',
    'What is the difference between React class components and functional components with hooks?',
    'Explain how the Linux kernel manages virtual memory and page tables.',
]


def _prompt_quality_metric(
    name: str,
    criteria: str,
    evaluation_params: list[SingleTurnParams] | None = None,
) -> GEval:
    return GEval(
        name=name,
        criteria=criteria,
        evaluation_params=evaluation_params or [SingleTurnParams.ACTUAL_OUTPUT],
        threshold=0.5,
        model=OPENAI_REVIEWER_MODEL,
    )


EXPLAINER_SPECIFIC_METRICS = [
    _prompt_quality_metric(
        'KaTeX Usage',
        'Does the response render mathematical expressions using KaTeX notation ($...$ or ' +
        '$$...$$) when appropriate?',
        [SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    ),
    _prompt_quality_metric(
        'Mermaid Diagram Usage',
        'Does the response include Mermaid diagram code blocks when describing architecture or ' +
        'workflows?',
        [SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    ),
    _prompt_quality_metric(
        'No Emojis',
        'Does the response avoid emojis?',
        [SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    ),
    _prompt_quality_metric(
        'No Personality Language',
        "Does the response avoid complimentary or apologetic language (no 'Great question!', " +
        "'Sorry about that', etc.)?",
        [SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    ),
]


def _make_test_case(
    question: str,
    actual: str,
    expected: str = '',
    context: list[str] | None = None,
) -> LLMTestCase:
    return LLMTestCase(
        input=question,
        actual_output=actual,
        expected_output=expected,
        context=context or [],
    )


class TestPromptStructure(TestCase):
    def test_explainer(self) -> None:
        self._assert_prompt_structure('Explainer', EXPLAINER_FULL)
        self.assertIn('katex', EXPLAINER_FULL.lower())
        self.assertIn('mermaid', EXPLAINER_FULL.lower())
        self.assertIn('no personality', EXPLAINER_FULL.lower())
        self.assertIn('emojis are unacceptable', EXPLAINER_FULL.lower())

    def test_ask(self) -> None:
        self._assert_prompt_structure('Ask', ASK_FULL)

    def test_explainer_has_extra_constraints(self) -> None:
        self.assertGreater(len(EXPLAINER_FULL), len(ASK_FULL))

    def _assert_prompt_structure(self, name: str, prompt: str) -> None:
        lowered = prompt.lower()
        self.assertIn('you are', lowered, f'{name}: missing role definition ("You are ...")')
        self.assertIn('read-only', lowered, f'{name}: missing read-only constraint')
        self.assertIn('never', lowered, f'{name}: missing explicit prohibition ("NEVER ...")')
        self.assertIn('workflow', lowered, f'{name}: missing workflow section')


class TestResponseQuality(TestCase):
    def test_explainer_specific_rules(self) -> None:
        question = \
            'Explain the architecture of the Flask web framework and describe the flow ' + \
            'of an HTTP request from the WSGI server through to a route handler response.'
        case = _make_test_case(question, _query(EXPLAINER_PROMPT, question))
        for metric in EXPLAINER_SPECIFIC_METRICS:
            assert_test(case, [metric], run_async=False)

    def test_question1(self) -> None:
        self._assert_responses(QUESTIONS[0])

    def test_question2(self) -> None:
        self._assert_responses(QUESTIONS[1])

    def test_question3(self) -> None:
        self._assert_responses(QUESTIONS[2])

    @staticmethod
    def _assert_responses(question: str) -> None:
        explainer_output = _query(EXPLAINER_PROMPT, question)
        ask_output = _query(ASK_PROMPT, question)
        relevancy = \
            AnswerRelevancyMetric(
                threshold=0.5,
                model=OPENAI_REVIEWER_MODEL,
                include_reason=True,
            )
        assert_test(
            _make_test_case(question, explainer_output),
            [relevancy],
            run_async=False,
        )
        assert_test(
            _make_test_case(question, ask_output),
            [relevancy],
            run_async=False,
        )


if __name__ == '__main__':
    main()
