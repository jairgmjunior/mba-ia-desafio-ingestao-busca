from search import search_prompt


def main():
    ask = search_prompt()

    if not ask:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Faça sua pergunta:\n")

    while True:
        try:
            pergunta = input("PERGUNTA: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not pergunta:
            continue

        if pergunta.lower() in {"sair", "exit", "quit"}:
            break

        resposta = ask(pergunta)
        print(f"RESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()
