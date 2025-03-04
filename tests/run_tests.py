import os
import subprocess
import sys
import argparse


def run_tests(test_type="all", verbose=False):
    """
    Executa os testes de acordo com o tipo especificado.
    
    Parameters
    ----------
    test_type : str
        Tipo de teste a ser executado: 'unit', 'integration' ou 'all'.
    verbose : bool
        Se True, exibe mais detalhes sobre os testes.
    """
    # Diretório raiz do projeto
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Parâmetros básicos do pytest
    pytest_args = ["pytest"]
    
    # Adiciona verbose se necessário
    if verbose:
        pytest_args.append("-v")
    
    # Adiciona cobertura de código
    pytest_args.extend(["--cov=.", "--cov-report=term", "--cov-report=html"])
    
    # Adiciona a exibição de progresso dos testes
    pytest_args.append("-xvs")
    
    # Determina quais testes executar
    if test_type == "unit":
        pytest_args.append("tests/unit/")
    elif test_type == "integration":
        pytest_args.append("tests/integration/")
    elif test_type == "all":
        pytest_args.append("tests/")
    else:
        print(f"Tipo de teste inválido: {test_type}")
        return 1
    
    # Muda para o diretório raiz e executa os testes
    os.chdir(root_dir)
    return subprocess.call(pytest_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa os testes da aplicação.")
    parser.add_argument("--type", choices=["unit", "integration", "all"], 
                        default="all", help="Tipo de teste a ser executado.")
    parser.add_argument("--verbose", action="store_true", 
                        help="Exibe informações detalhadas sobre os testes.")
    
    args = parser.parse_args()
    sys.exit(run_tests(args.type, args.verbose)) 