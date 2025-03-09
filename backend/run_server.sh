#!/bin/bash

# Mensaje de ayuda
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -e, --environment <env>  Especifica el environment de trabajo (production, development, or test)"
    echo "  --no-persistence         Borra la base de datos del environment"
    echo "  -h, --help               Mostrar el mensaje de ayuda"
}

# Default values
ENVIRONMENT="development"
NO_PERSISTENCE=false
PYTHONPATH=$(pwd)

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --no-persistence)
            NO_PERSISTENCE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(production|development|test)$ ]]; then
    echo "Error: Invalid environment. Choose production, development, or test."
    exit 1
fi

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Wait for venv to activate
sleep 1

# Export environment variable
export ENVIRONMENT

# Start Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload


# Delete database if --no-persistence is set
if [ "$NO_PERSISTENCE" = true ]; then
    DB_FILE="database_${ENVIRONMENT}.sqlite"
    if [ -f "$DB_FILE" ]; then
        echo "Deleting database: $DB_FILE"
        rm "$DB_FILE"
    else
        echo "Database file not found: $DB_FILE"
    fi
fi

# Unset environment variable
unset ENVIRONMENT

# Deactivate virtual environment
deactivate
