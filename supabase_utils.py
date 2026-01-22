"""
Supabase Integration Utility for Django

Fournit des utilitaires pour utiliser Supabase avec Django
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from django.conf import settings
from django.db import connection


class SupabaseManager:
    """
    Gestionnaire pour les opérations Supabase
    
    Usage:
        sb = SupabaseManager()
        data = sb.select_all('table_name')
    """
    
    _client: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Optional[Client]:
        """Obtenir ou créer le client Supabase"""
        if cls._client is None:
            supabase_url = getattr(settings, 'SUPABASE_URL', None)
            supabase_key = getattr(settings, 'SUPABASE_KEY', None)
            
            if supabase_url and supabase_key:
                cls._client = create_client(supabase_url, supabase_key)
        
        return cls._client
    
    @classmethod
    def is_using_supabase(cls) -> bool:
        """Vérifier si on utilise Supabase"""
        return os.environ.get('USE_SUPABASE', 'false').lower() == 'true'
    
    @classmethod
    def get_db_info(cls) -> Dict[str, Any]:
        """Obtenir les infos de la BD actuelle"""
        db_config = connection.settings_dict
        return {
            'engine': db_config.get('ENGINE', 'unknown'),
            'host': db_config.get('HOST', 'localhost'),
            'port': db_config.get('PORT', 'N/A'),
            'database': db_config.get('NAME', 'unknown'),
            'user': db_config.get('USER', 'unknown'),
            'is_supabase': cls.is_using_supabase(),
        }
    
    @classmethod
    def select_all(cls, table_name: str, columns: str = "*") -> list:
        """
        Sélectionner tous les enregistrements
        
        Args:
            table_name: Nom de la table
            columns: Colonnes à récupérer (défaut: *)
            
        Returns:
            Liste des enregistrements
        """
        client = cls.get_client()
        if not client:
            raise Exception("Supabase client not configured")
        
        response = client.table(table_name).select(columns).execute()
        return response.data
    
    @classmethod
    def select_one(cls, table_name: str, column: str, value: Any) -> Optional[Dict]:
        """
        Sélectionner un enregistrement
        
        Args:
            table_name: Nom de la table
            column: Colonne de filtre
            value: Valeur du filtre
            
        Returns:
            Un enregistrement ou None
        """
        client = cls.get_client()
        if not client:
            raise Exception("Supabase client not configured")
        
        response = (
            client.table(table_name)
            .select("*")
            .eq(column, value)
            .maybe_single()
            .execute()
        )
        return response.data
    
    @classmethod
    def insert(cls, table_name: str, data: Dict) -> Dict:
        """
        Insérer un enregistrement
        
        Args:
            table_name: Nom de la table
            data: Données à insérer
            
        Returns:
            L'enregistrement créé
        """
        client = cls.get_client()
        if not client:
            raise Exception("Supabase client not configured")
        
        response = client.table(table_name).insert(data).execute()
        return response.data[0] if response.data else None
    
    @classmethod
    def update(cls, table_name: str, column: str, value: Any, data: Dict) -> Dict:
        """
        Mettre à jour un enregistrement
        
        Args:
            table_name: Nom de la table
            column: Colonne de filtre
            value: Valeur du filtre
            data: Données à mettre à jour
            
        Returns:
            L'enregistrement mis à jour
        """
        client = cls.get_client()
        if not client:
            raise Exception("Supabase client not configured")
        
        response = (
            client.table(table_name)
            .update(data)
            .eq(column, value)
            .execute()
        )
        return response.data[0] if response.data else None
    
    @classmethod
    def delete(cls, table_name: str, column: str, value: Any) -> bool:
        """
        Supprimer un enregistrement
        
        Args:
            table_name: Nom de la table
            column: Colonne de filtre
            value: Valeur du filtre
            
        Returns:
            True si suppression réussie
        """
        client = cls.get_client()
        if not client:
            raise Exception("Supabase client not configured")
        
        response = (
            client.table(table_name)
            .delete()
            .eq(column, value)
            .execute()
        )
        return True


# Exemple d'utilisation dans manage.py
if __name__ == '__main__':
    manager = SupabaseManager()
    
    print("=== Database Info ===")
    for key, value in manager.get_db_info().items():
        print(f"{key}: {value}")
