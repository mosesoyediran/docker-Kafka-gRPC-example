import socket
from functools import lru_cache
from typing import Dict, List

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    GRPC_PORT : int
    
    # ── Kafka infra ──────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: List[str] = Field(
        default_factory=lambda: ["kafka1:9092"]
    )
    
    # default fallbacks if a service isn’t in your YAML
    KAFKA_GROUP_ID: str = Field(
        default="default-group",
        description="Fallback consumer group if not specified in kafka_topics.yml",
    )

    
    KAFKA_CLIENT_ID: str = Field(
        default_factory=lambda: f"svc-{socket.gethostname()}",
        description="Fallback client_id if not specified in kafka_topics.yml",
    )
    
    
    
    SERVICE_NAME: str = Field("default", env="SERVICE_NAME")
    
    KAFKA_TOPICS_FILE: str 
    
    KAFKA_TOPIC_DLQ: str = Field("kafka.dlq")         # universal DLQ topic
    GATEWAY_RPS_LIMIT: int = Field(200)  

    @property
    def KAFKA_CATALOG(self) -> dict[str, dict]:
        """
        Loads the central Kafka topics/catalog file.
        """
        with open(self.KAFKA_TOPICS_FILE, "r") as f:
            return yaml.safe_load(f)
    
    @field_validator("KAFKA_BOOTSTRAP_SERVERS", mode="before")
    def _split_bootstrap(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def kafka_topics(self) -> dict[str, str]:
        """All topics the service knows about."""
        return {
            k.removeprefix("KAFKA_TOPIC_"): v
            for k, v in self.model_dump().items()
            if k.startswith("KAFKA_TOPIC_") and v
        }
    
    
    def kafka_producer_config(self) -> dict[str, str]:
        """
        Configuration for aiokafka AIOKafkaProducer.
        """
        cat = self.KAFKA_CATALOG.get(self.SERVICE_NAME, {})
        return {
            "bootstrap_servers": ",".join(self.KAFKA_BOOTSTRAP_SERVERS),
            "client_id": cat.get("client_id", self.KAFKA_CLIENT_ID),
        }

    @property
    def kafka_consumer_config(self) -> dict[str, str]:
        """
        Base config for aiokafka AIOKafkaConsumer (without topics).
        """
        cat = self.KAFKA_CATALOG.get(self.SERVICE_NAME, {})
        
        return {
            "bootstrap_servers": ",".join(self.KAFKA_BOOTSTRAP_SERVERS),
            "group_id": cat.get("group_id", None) or self.KAFKA_GROUP_ID,
            "client_id": cat.get("client_id", self.KAFKA_CLIENT_ID),
        }

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:  # noqa: D401
    return Settings()


settings = get_settings()
