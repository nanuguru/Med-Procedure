"""
Search Tools - Google Search, OpenAI, DuckDuckGo, and other search platforms
"""
from typing import Dict, Any, List, Optional
import httpx
import structlog
from config import settings

logger = structlog.get_logger()


class GoogleSearchTool:
    """Google Search tool using SerpAPI"""
    
    def __init__(self):
        self.api_key = settings.serpapi_api_key
        self.base_url = "https://serpapi.com/search"
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        setting: str = "Hospital"
    ) -> Dict[str, Any]:
        """
        Search Google for clinical procedures
        
        Args:
            query: Search query
            num_results: Number of results to return
            setting: Hospital or Home setting context
        """
        if not self.api_key:
            logger.warning("SerpAPI key not configured, using fallback")
            return await self._fallback_search(query, setting)
        
        try:
            # Enhance query with setting context
            enhanced_query = f"{query} clinical procedure {setting} setting nursing"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "q": enhanced_query,
                        "api_key": self.api_key,
                        "num": num_results,
                        "engine": "google"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract relevant information
                results = []
                if "organic_results" in data:
                    for item in data["organic_results"][:num_results]:
                        results.append({
                            "title": item.get("title", ""),
                            "link": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "source": "google_search"
                        })
                
                return {
                    "success": True,
                    "query": enhanced_query,
                    "results": results,
                    "total_results": len(results)
                }
                
        except Exception as e:
            logger.error("Google search error", error=str(e), exc_info=True)
            return await self._fallback_search(query, setting)
    
    async def _fallback_search(self, query: str, setting: str) -> Dict[str, Any]:
        """Fallback search when API is not available"""
        return {
            "success": False,
            "query": query,
            "results": [],
            "message": "Search API not configured",
            "fallback": True
        }


class GroqSearchTool:
    """Groq-based search and information retrieval using Llama models"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'groq_api_key', None)
        # Use llama-3.3-70b-versatile (latest) or llama-3.1-8b-instant (faster)
        # Available models: llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768
        self.model = "llama-3.3-70b-versatile"  # Latest model, can also use "llama-3.1-8b-instant" for faster responses
    
    async def search_procedures(
        self,
        service_name: str,
        setting: str = "Hospital"
    ) -> Dict[str, Any]:
        """
        Use Groq to get clinical procedures for a service
        
        Args:
            service_name: Name of the service/procedure
            setting: Hospital or Home setting
        """
        if not self.api_key:
            logger.warning("Groq API key not configured")
            return {
                "success": False,
                "message": "Groq API key not configured"
            }
        
        try:
            try:
                from groq import AsyncGroq
            except ImportError:
                logger.error("Groq library not installed")
                return {
                    "success": False,
                    "message": "Groq library not installed. Install with: pip install groq"
                }
            
            client = AsyncGroq(api_key=self.api_key)
            
            prompt = f"""You are a clinical procedure expert. Provide detailed, step-by-step procedures for: {service_name}

Setting: {setting}

Please provide:
1. Pre-procedure preparation
2. Required equipment and supplies
3. Step-by-step procedure
4. Safety considerations
5. Post-procedure care
6. Common complications and how to address them

Format the response as a structured procedure guide suitable for nurses and certified home-health caregivers.
Important: Do not provide medical diagnoses or prescriptions. Focus on procedural steps and safety protocols."""

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a clinical procedure expert helping nurses and caregivers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            return {
                "success": True,
                "service_name": service_name,
                "setting": setting,
                "procedures": content,
                "source": "groq",
                "model": self.model
            }
            
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            # Check for specific error types
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                error_msg = "Groq API rate limit exceeded. Please check your usage at https://console.groq.com/"
            elif "model" in error_msg.lower() and ("not found" in error_msg.lower() or "decommissioned" in error_msg.lower()):
                error_msg = f"Groq model not available: {self.model}. Try using 'llama-3.1-8b-instant' or 'llama-3.3-70b-versatile' instead."
            elif "api key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                error_msg = "Invalid Groq API key. Please check your API key at https://console.groq.com/keys"
            
            logger.error("Groq search error", error=error_msg, error_type=error_type)
            return {
                "success": False,
                "error": error_msg,
                "error_type": error_type
            }


class DuckDuckGoSearchTool:
    """DuckDuckGo Search tool - Free, no API key required"""
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        setting: str = "Hospital"
    ) -> Dict[str, Any]:
        """
        Search DuckDuckGo for clinical procedures
        
        Args:
            query: Search query
            num_results: Number of results to return
            setting: Hospital or Home setting context
        """
        try:
            import warnings
            # Suppress the deprecation warning about package rename
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning)
                try:
                    from duckduckgo_search import DDGS
                except ImportError:
                    # Try the new package name
                    from ddgs import DDGS
            
            # Enhance query with setting context
            enhanced_query = f"{query} clinical procedure {setting} setting nursing"
            
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(
                    enhanced_query,
                    max_results=num_results
                )
                
                for item in search_results:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("href", ""),
                        "snippet": item.get("body", ""),
                        "source": "duckduckgo"
                    })
            
            return {
                "success": True,
                "query": enhanced_query,
                "results": results,
                "total_results": len(results)
            }
            
        except ImportError:
            logger.warning("duckduckgo-search not installed")
            return {
                "success": False,
                "query": query,
                "results": [],
                "message": "DuckDuckGo search library not installed"
            }
        except Exception as e:
            logger.error("DuckDuckGo search error", error=str(e), exc_info=True)
            return {
                "success": False,
                "query": query,
                "results": [],
                "error": str(e)
            }


class HybridSearchTool:
    """Combines multiple search tools for comprehensive results"""
    
    def __init__(self):
        self.google_search = GoogleSearchTool()
        self.groq_search = GroqSearchTool()
        self.duckduckgo_search = DuckDuckGoSearchTool()
    
    async def search(
        self,
        service_name: str,
        setting: str = "Hospital"
    ) -> Dict[str, Any]:
        """
        Perform hybrid search using multiple tools
        
        Args:
            service_name: Name of the service/procedure
            setting: Hospital or Home setting
        """
        results = {
            "service_name": service_name,
            "setting": setting,
            "sources": {}
        }
        
        # Try Groq first (fast and high quality), then fallback to free search
        groq_results = await self.groq_search.search_procedures(
            service_name,
            setting=setting
        )
        results["sources"]["groq"] = groq_results
        
        # Use DuckDuckGo as primary free search (no API key needed)
        duckduckgo_results = await self.duckduckgo_search.search(
            f"{service_name} nursing procedure",
            setting=setting
        )
        results["sources"]["duckduckgo"] = duckduckgo_results
        
        # Try Google Search if API key is available (optional)
        google_results = await self.google_search.search(
            f"{service_name} nursing procedure",
            setting=setting
        )
        results["sources"]["google"] = google_results
        
        # Combine and synthesize results
        # Prioritize Groq if successful, otherwise use DuckDuckGo
        combined_procedures = self._synthesize_results(
            google_results,
            groq_results,
            duckduckgo_results,
            service_name,
            setting
        )
        
        results["procedures"] = combined_procedures
        results["success"] = True
        
        return results
    
    def _synthesize_results(
        self,
        google_results: Dict[str, Any],
        groq_results: Dict[str, Any],
        duckduckgo_results: Dict[str, Any],
        service_name: str,
        setting: str
    ) -> Dict[str, Any]:
        """Synthesize results from multiple sources"""
        procedures = {
            "service_name": service_name,
            "setting": setting,
            "sources_used": [],
            "detailed_procedure": None,
            "references": []
        }
        
        # Use Groq results as primary if available (fast and high quality)
        if groq_results.get("success") and "procedures" in groq_results:
            procedures["detailed_procedure"] = groq_results["procedures"]
            procedures["sources_used"].append("groq")
            logger.info("Using Groq results for procedure details")
        
        # Add DuckDuckGo search references (free, always available)
        if duckduckgo_results.get("success") and "results" in duckduckgo_results:
            if not procedures["detailed_procedure"]:
                # If no OpenAI result, create a summary from DuckDuckGo results
                snippets = [r.get("snippet", "") for r in duckduckgo_results["results"][:5] if r.get("snippet")]
                if snippets:
                    procedures["detailed_procedure"] = self._create_procedure_from_snippets(
                        snippets, service_name, setting
                    )
                    logger.info("Created procedure from DuckDuckGo snippets", snippet_count=len(snippets))
                else:
                    # Fallback: create basic procedure structure from search results
                    procedures["detailed_procedure"] = self._create_basic_procedure(
                        duckduckgo_results["results"], service_name, setting
                    )
                    logger.info("Created basic procedure from DuckDuckGo results")
            procedures["references"].extend(duckduckgo_results["results"])
            if "duckduckgo" not in procedures["sources_used"]:
                procedures["sources_used"].append("duckduckgo")
        
        # Add Google search references if available
        if google_results.get("success") and "results" in google_results:
            procedures["references"].extend(google_results["results"])
            if "google" not in procedures["sources_used"]:
                procedures["sources_used"].append("google")
        
        return procedures
    
    def _create_procedure_from_snippets(
        self,
        snippets: List[str],
        service_name: str,
        setting: str
    ) -> str:
        """Create a procedure summary from search snippets"""
        if not snippets:
            return self._create_basic_procedure([], service_name, setting)
        
        combined = "\n\n".join([f"• {s}" for s in snippets[:5] if s.strip()])
        return f"""Clinical Procedure: {service_name}
Setting: {setting}

Based on available resources:

{combined}

Note: This is a summary compiled from search results. For complete and verified procedures, please consult official clinical guidelines and protocols."""

    def _create_basic_procedure(
        self,
        results: List[Dict[str, Any]],
        service_name: str,
        setting: str
    ) -> str:
        """Create a basic procedure structure when no detailed info is available"""
        references_text = ""
        if results:
            ref_list = [f"• {r.get('title', '')} - {r.get('link', '')}" for r in results[:5]]
            references_text = "\n".join(ref_list)
        
        return f"""Clinical Procedure: {service_name}
Setting: {setting}

Procedure Overview:
This procedure should be performed following standard clinical protocols for {service_name} in a {setting} environment.

Key Considerations:
- Ensure proper hygiene and infection control measures
- Follow aseptic technique where applicable
- Document all steps and patient responses
- Maintain patient privacy and comfort

For detailed step-by-step instructions, please refer to the reference materials provided below.

References:
{references_text if references_text else "Please consult official clinical guidelines and protocols for detailed procedures."}

Note: This information is compiled from search results. Always follow your institution's protocols and guidelines."""

