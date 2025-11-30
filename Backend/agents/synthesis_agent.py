"""
Synthesis Agent - Synthesizes and formats final procedure output
"""
from typing import Dict, Any
import structlog
from agents.base_agent import BaseAgent
from config import settings

logger = structlog.get_logger()


class SynthesisAgent(BaseAgent):
    """Agent responsible for synthesizing final procedure output"""
    
    def __init__(self, agent_id: str = "synthesis_agent_1"):
        super().__init__(agent_id, "synthesis")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute synthesis of procedure data"""
        self.status = "synthesizing"
        self.log_action("start_synthesis", input_data)
        
        try:
            search_results = input_data.get("search_results", {})
            validation_results = input_data.get("validation_results", {})
            service_name = input_data.get("service_name", "")
            setting = input_data.get("setting", "Hospital")
            
            # Synthesize final output
            final_procedure = {
                "service_name": service_name,
                "setting": setting,
                "procedure_details": None,
                "validation": {},
                "equipment": {},
                "sources": [],
                "generated_at": input_data.get("timestamp")
            }
            
            # Add search results
            if search_results.get("success"):
                search_data = search_results.get("results", {})
                logger.info("Synthesis: processing search data", has_search_data=bool(search_data), search_data_keys=list(search_data.keys()) if isinstance(search_data, dict) else "not_dict")
                
                procedures = search_data.get("procedures", {})
                logger.info("Synthesis: procedures object", has_procedures=bool(procedures), procedures_type=type(procedures).__name__, procedures_keys=list(procedures.keys()) if isinstance(procedures, dict) else "not_dict")
                
                # Extract procedure details - this is the primary source
                detailed_procedure = None
                
                if procedures and isinstance(procedures, dict):
                    detailed_procedure = procedures.get("detailed_procedure")
                    logger.info("Synthesis: from procedures", has_detailed=bool(detailed_procedure), detailed_type=type(detailed_procedure).__name__ if detailed_procedure else "None")
                    
                    if detailed_procedure:
                        final_procedure["procedure_details"] = detailed_procedure
                        final_procedure["sources"] = procedures.get("sources_used", [])
                        if "references" in procedures:
                            final_procedure["references"] = procedures["references"]
                        logger.info("Synthesis: successfully extracted procedure_details from procedures object")
                
                # Fallback: try to get from Groq source directly
                if not detailed_procedure:
                    sources = search_data.get("sources", {})
                    groq_source = sources.get("groq", {})
                    logger.info("Synthesis: checking Groq source", has_source=bool(groq_source), source_success=groq_source.get("success"))
                    
                    if groq_source.get("success") and "procedures" in groq_source:
                        final_procedure["procedure_details"] = groq_source["procedures"]
                        final_procedure["sources"] = ["groq"]
                        logger.info("Synthesis: extracted from Groq source", has_procedure=bool(groq_source["procedures"]))
                    else:
                        # Fallback to DuckDuckGo if OpenAI failed
                        duckduckgo_source = sources.get("duckduckgo", {})
                        logger.info("Synthesis: checking DuckDuckGo source", has_source=bool(duckduckgo_source), source_success=duckduckgo_source.get("success"))
                        
                        # DuckDuckGo results should be in procedures.detailed_procedure
                        if procedures and isinstance(procedures, dict):
                            if procedures.get("detailed_procedure"):
                                final_procedure["procedure_details"] = procedures["detailed_procedure"]
                                final_procedure["sources"] = procedures.get("sources_used", ["duckduckgo"])
                                if "references" in procedures:
                                    final_procedure["references"] = procedures["references"]
                                logger.info("Synthesis: using DuckDuckGo results from procedures")
                            elif duckduckgo_source.get("success") and "results" in duckduckgo_source:
                                # Last resort: create from DuckDuckGo results directly
                                snippets = [r.get("snippet", "") for r in duckduckgo_source["results"][:5] if r.get("snippet")]
                                if snippets:
                                    from tools.search_tools import HybridSearchTool
                                    tool = HybridSearchTool()
                                    final_procedure["procedure_details"] = tool._create_procedure_from_snippets(
                                        snippets, service_name, setting
                                    )
                                    final_procedure["sources"] = ["duckduckgo"]
                                    final_procedure["references"] = duckduckgo_source["results"]
                                    logger.info("Synthesis: created procedure from DuckDuckGo snippets directly")
            else:
                logger.warning("Synthesis: search results not successful", search_success=search_results.get("success"))
            
            # Add validation results
            if validation_results.get("success"):
                final_procedure["validation"] = validation_results.get("validation", {})
                final_procedure["equipment"] = validation_results.get("equipment", {})
                
                # Merge enhanced procedure
                enhanced = validation_results.get("enhanced_procedure", {})
                if enhanced:
                    final_procedure["context"] = enhanced.get("context", {})
            
            self.status = "completed"
            self.log_action("synthesis_completed")
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "final_procedure": final_procedure
            }
            
        except Exception as e:
            self.status = "error"
            self.log_action("synthesis_error", {"error": str(e)})
            logger.error("Synthesis agent error", error=str(e), exc_info=True)
            return {
                "success": False,
                "agent_id": self.agent_id,
                "error": str(e)
            }

