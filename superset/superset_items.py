import json


class DashboardItems:

    #TODO: Update the this function to take parameters you want modified in the chart
    @staticmethod
    def create_chart():
        """
        Generates a superset chart.
        
        Returns:
            json: A json body containing the configuration settings for a chart.
                  This configuration includes details like cache timeouts, datasource info,
                  description, external URLs, ownership, and visualization settings.
        """
        return{
            "cache_timeout": 0,
            "certification_details": "",
            "certified_by": "",
            "dashboards": [1],
            "datasource_id": 1,
            "datasource_name": "main.test_table",
            "datasource_type": "table",
            "description": "This chart displays video data from YouTube.",
            "external_url": "string",
            "is_managed_externally": True,
            "owners": [1],
            "params": "{\"datasource\": \"main.test_table\", \"viz_type\": \"table\", \"url_params\": {}, \"granularity_sqla\": null, \"time_grain_sqla\": null, \"time_range\": \"No filter\", \"groupby\": [], \"metrics\": [], \"all_columns\": [\"Video URL\", \"Video Title\", \"Channel Title\", \"Date\"], \"percent_metrics\": [], \"row_limit\": 1000, \"include_time\": false, \"order_desc\": true}",
            "query_context": "{}",
            "query_context_generation": False,
            "slice_name": "string",
            "viz_type": "table"
        }


    

    
    #TODO: Update this function to take parameters you want modified when creating a dashboard
    @staticmethod
    def create_dashboard():
        """
        Generates the configuration for a new dashboard.
        
        Returns:
            json: A json body containing the settings for creating a new dashboard.
                  It includes details like the dashboard title, publication status, and ownership.
        
        """

        return {
        "dashboard_title": "My New Dashboard",
        "published": True,
        "slug": "my-new-dashboard",
        "position_json": "{}",
        "css": "",
        "json_metadata": "",
        "owners": [1]
    }

    
    #TODO: "Update the dashboard layout to include the new chart in the layout you want"
    #TODO: "Update function args to pass the items you want to update"
    @staticmethod
    def update_dashboard(json):
        """
        Updates the configuration of an existing dashboard, including any new objects.
        
        Args:
            json (str): JSON string that includes the details of the objects to be added to the dashboard.
        
        Returns:
            json: A json body with the updated settings for the dashboard.
        
        """

        return {
            
            "certification_details": "",
            "certified_by": "",
            "css": "",
            "dashboard_title": "My New Dashboard",
            "external_url": "http://localhost:8088/superset/dashboard/my-new-dashboard",
            "is_managed_externally": True,
            "json_metadata": json,
            "owners": [
                1
            ],
            "position_json": "",
            "published": False,
            "roles": [

            ],
            "slug": "my-new-dashboard"     
    }


    @staticmethod
    def create_dataset():
        return{
            "always_filter_main_dttm": False,
            "database": 1,
            "external_url": "",
            "is_managed_externally": True,
            "normalize_columns": False,
            "owners": [
                1
            ],
            "schema": "main.test_table",
            "sql": "SELECT * FROM main.test_table",
            "table_name": "yeeer"
        }
