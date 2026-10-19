def recent_chat_messages(messages, max_messages=40):
    """Keep the system prompt and a bounded recent conversation window."""
    if max_messages < 1:
        raise ValueError("max_messages must be at least 1.")

    system_message = None
    conversation = messages
    if messages and messages[0].get("role") == "system":
        system_message = messages[0]
        conversation = messages[1:]

    recent_messages = conversation[-max_messages:]
    if system_message is not None:
        return [system_message, *recent_messages]
    return list(recent_messages)


def infer_adaptive_profile(messages, max_messages=8):
    """Detect patterns in recent user messages and adapt the assistant style."""
    recent_user_messages = [
        message.get("content", "")
        for message in messages[-max_messages:]
        if message.get("role") == "user"
        and isinstance(message.get("content"), str)
    ]

    if not recent_user_messages:
        return (
            "The user is open to a balanced assistant style with clear "
            "reasoning, practical next steps, and thoughtful follow-up questions."
        )

    combined = "\n".join(recent_user_messages).lower()
    signals = []

    if any(
        phrase in combined
        for phrase in [
            "brief",
            "quick",
            "concise",
            "short answer",
            "simple answer",
            "just answer",
            "in one sentence",
            "give me the gist",
        ]
    ):
        signals.append("The user prefers brief, focused answers.")

    if any(
        phrase in combined
        for phrase in [
            "step by step",
            "walk me through",
            "explain it clearly",
            "how do i",
            "break it down",
            "compare options",
            "why",
        ]
    ):
        signals.append(
            "The user likes structured explanations and clear progression."
        )

    if any(
        phrase in combined
        for phrase in [
            "example",
            "show me",
            "debug",
            "code",
            "implementation",
            "prototype",
            "plan",
        ]
    ):
        signals.append(
            "The user responds well to concrete examples and practical detail."
        )

    if any(
        phrase in combined
        for phrase in [
            "be direct",
            "no fluff",
            "honest",
            "don't sugarcoat",
            "straight answer",
        ]
    ):
        signals.append("The user values direct, honest, no-nonsense guidance.")

    if any(
        phrase in combined
        for phrase in [
            "friendly",
            "warm",
            "encouraging",
            "supportive",
            "gentle",
        ]
    ):
        signals.append("The user prefers a warm, supportive tone.")

    if any(
        phrase in combined
        for phrase in [
            "formal",
            "professional",
            "polished",
            "reports",
            "email",
            "executive",
        ]
    ):
        signals.append("The user prefers polished, professional wording.")

    if not signals:
        signals.append(
            "The user is open to a balanced assistant style with clear "
            "reasoning, practical next steps, and thoughtful follow-up."
        )

    return " ".join(signals[:3])
