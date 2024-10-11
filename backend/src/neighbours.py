import logging
from src.graph_query import *

NEIGHBOURS_FROM_ELEMENT_ID_QUERY = """
MATCH (n) 
WHERE elementId(n) = $element_id

MATCH (n)<-[rels]->(m)  
WITH n, 
     ([n] + COLLECT(DISTINCT m)) AS allNodes, 
     COLLECT(DISTINCT rels) AS allRels

RETURN 
    [node IN allNodes | 
        node {
            .*,
            embedding: null,
            text: null,
            summary: null,
            labels: [coalesce(apoc.coll.removeAll(labels(node), ['__Entity__'])[0], "*")],
            elementId: elementId(node)
        }
    ] AS nodes,
    
    [r IN allRels | 
        {
            startNode: elementId(startNode(r)),
            endNode: elementId(endNode(r)),
            type: type(r)
            // elementId: elementId(r) // Uncomment if you need the elementId of the relationship
        }
    ] AS relationships
"""


def get_neighbour_nodes(uri, username, password, database, element_id, query=NEIGHBOURS_FROM_ELEMENT_ID_QUERY):
    driver = None

    try:
        logging.info(f"Querying neighbours for element_id: {element_id}")
        driver = get_graphDB_driver(uri, username, password, database)
        driver.verify_connectivity()
        logging.info("Database connectivity verified.")

        records, summary, keys = driver.execute_query(query,element_id=element_id)
        nodes = records[0].get("nodes", [])
        relationships = records[0].get("relationships", [])
        result = {"nodes": nodes, "relationships": relationships}
        
        logging.info(f"Successfully retrieved neighbours for element_id: {element_id}")
        return result
    
    except Exception as e:
        logging.error(f"Error retrieving neighbours for element_id: {element_id}: {e}")
        return {"nodes": [], "relationships": []}
    
    finally:
        if driver is not None:
            driver.close()
            logging.info("Database driver closed.")