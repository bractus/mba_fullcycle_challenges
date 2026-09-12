from src.chat import process_ingestion, ask_question

def main():
    print("=== Sistema de Chat RAG ===")
    
    # 1. Ingestion Phase
    while True:
        do_ingest = input("\nVocê deseja inserir um arquivo PDF? (s/n): ").strip().lower()
        if do_ingest == 's':
            file_path = input("Digite o caminho completo para o arquivo PDF: ").strip()
            print(f"Processando {file_path}...")
            result = process_ingestion(file_path)
            print(result)
        elif do_ingest == 'n':
            break
        else:
            print("Por favor, responda 's' ou 'n'.")

    while True:

        print("Digite 'sair' para encerrar.")
        user_query = input("\nDigite sua pergunta: ").strip()
        
        if user_query.lower() in ('sair', 'exit', 'quit'):
            print("Tchau!")
            break
        
        if not user_query:
            continue

        print("Pensando...")
        answer = ask_question(user_query)
        
        print("\n=== Resposta ===")
        print(answer)
        print("===============")

if __name__ == "__main__":
    main()