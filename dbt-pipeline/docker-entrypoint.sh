#!/usr/bin/env bash
# Entrypoint for the prod dbt runner (Databricks).
# Commands: daily (default) | build | run | test | seed | dbt <args>

DBT_TARGET="${DBT_TARGET:-prod}"
ENABLE_ELEMENTARY="${ENABLE_ELEMENTARY:-true}"
DBT_FLAGS=(--profiles-dir . --project-dir .)

# --- Validate required Databricks credentials for the prod target ---
if [ "$DBT_TARGET" = "prod" ]; then
    missing=()
    [ -z "$DATABRICKS_HOST" ] && missing+=(DATABRICKS_HOST)
    [ -z "$DATABRICKS_HTTP_PATH" ] && missing+=(DATABRICKS_HTTP_PATH)
    [ -z "$DATABRICKS_TOKEN" ] && missing+=(DATABRICKS_TOKEN)
    if [ ${#missing[@]} -gt 0 ]; then
        echo "ERROR: missing required environment variables: ${missing[*]}" >&2
        exit 1
    fi
fi

COMMAND="${1:-daily}"

echo "=============================================="
echo " dbt runner"
echo "   target:     $DBT_TARGET"
echo "   command:    $COMMAND"
echo "   elementary: $ENABLE_ELEMENTARY"
echo "=============================================="

case "$COMMAND" in
    daily)
        FAILED=0

        dbt deps "${DBT_FLAGS[@]}" || FAILED=1

        # Seed first: staging models read seeds as sources (no DAG edge),
        # so a fresh database needs the raw tables before dbt build.
        dbt seed --target "$DBT_TARGET" "${DBT_FLAGS[@]}" || FAILED=1

        # Record build failure but continue so observability still runs.
        dbt build --target "$DBT_TARGET" "${DBT_FLAGS[@]}" || FAILED=1

        if [ "$ENABLE_ELEMENTARY" = "true" ]; then
            dbt run --select elementary --target "$DBT_TARGET" "${DBT_FLAGS[@]}" || FAILED=1
            edr report --profiles-dir . --profile-target "$DBT_TARGET" \
                --file-path /app/reports/elementary_report.html || FAILED=1
        fi

        if [ "$FAILED" -ne 0 ]; then
            echo "daily: one or more steps failed" >&2
            exit 1
        fi
        echo "daily: all steps succeeded"
        ;;

    build|run|test|seed)
        # shellcheck disable=SC2086
        dbt "$COMMAND" --target "$DBT_TARGET" "${DBT_FLAGS[@]}" $EXTRA_ARGS
        exit $?
        ;;

    dbt)
        shift
        dbt "$@" "${DBT_FLAGS[@]}"
        exit $?
        ;;

    *)
        echo "Unknown command: $COMMAND" >&2
        echo "Usage: docker run <image> [daily|build|run|test|seed|dbt <args>]" >&2
        echo "  daily        dbt deps + build, then Elementary report (default)" >&2
        echo "  build        dbt build   (EXTRA_ARGS appended)" >&2
        echo "  run          dbt run     (EXTRA_ARGS appended)" >&2
        echo "  test         dbt test    (EXTRA_ARGS appended)" >&2
        echo "  seed         dbt seed    (EXTRA_ARGS appended)" >&2
        echo "  dbt <args>   pass args straight to dbt" >&2
        exit 1
        ;;
esac
