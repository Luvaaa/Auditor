"""Graph insights module - OPTIONAL interpretive analysis for dependency graphs.

This module provides interpretive metrics like health scores, recommendations,
and weighted rankings. It's completely optional and decoupled from core graph
analysis - similar to how ml.py works.

IMPORTANT: This module performs interpretation and scoring, which goes beyond
pure data extraction. It's designed for teams that want actionable insights
and are willing to accept some subjective analysis.
"""

from collections import defaultdict
from typing import Any


class GraphInsights:
    """Optional graph interpretation and scoring.
    
    This class provides subjective metrics and recommendations based on
    graph topology. All methods here involve interpretation and scoring,
    not just raw data extraction.
    """
    
    # Weights for hotspot scoring (configurable)
    DEFAULT_WEIGHTS = {
        "in_degree": 0.3,
        "out_degree": 0.2,
        "centrality": 0.3,
        "churn": 0.1,
        "loc": 0.1,
    }
    
    def __init__(self, weights: dict[str, float] | None = None):
        """
        Initialize insights analyzer with optional weight configuration.
        
        Args:
            weights: Custom weights for hotspot scoring
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
    
    def rank_hotspots(
        self, 
        import_graph: dict[str, Any], 
        call_graph: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Rank nodes by their importance as hotspots using weighted scoring.
        
        This is an INTERPRETIVE method that assigns subjective importance
        scores based on configurable weights.
        
        Args:
            import_graph: Import/dependency graph
            call_graph: Optional call graph for additional signals
            
        Returns:
            List of hotspot nodes sorted by interpreted score
        """
        # Calculate in/out degrees for import graph
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        
        for edge in import_graph.get("edges", []):
            out_degree[edge["source"]] += 1
            in_degree[edge["target"]] += 1
        
        # Add call graph degrees if available
        if call_graph:
            for edge in call_graph.get("edges", []):
                out_degree[edge["source"]] += 1
                in_degree[edge["target"]] += 1
        
        # Calculate centrality (simplified betweenness centrality approximation)
        centrality = self._calculate_centrality(import_graph)
        
        # Build node metrics with INTERPRETED SCORING
        hotspots = []
        for node in import_graph.get("nodes", []):
            node_id = node["id"]
            
            # Normalize metrics
            in_deg = in_degree[node_id]
            out_deg = out_degree[node_id]
            cent = centrality.get(node_id, 0)
            churn = node.get("churn", 0) or 0
            loc = node.get("loc", 0) or 0
            
            # INTERPRETATION: Calculate weighted score
            score = (
                self.weights["in_degree"] * in_deg +
                self.weights["out_degree"] * out_deg +
                self.weights["centrality"] * cent +
                self.weights["churn"] * (churn / 100) +  # Normalize churn
                self.weights["loc"] * (loc / 1000)  # Normalize LOC
            )
            
            hotspots.append({
                "id": node_id,
                "in_degree": in_deg,
                "out_degree": out_deg,
                "centrality": cent,
                "churn": churn,
                "loc": loc,
                "score": score,  # INTERPRETED METRIC
            })
        
        # Sort by interpreted score (highest first)
        hotspots.sort(key=lambda h: h["score"], reverse=True)
        
        return hotspots
    
    def _calculate_centrality(self, graph: dict[str, Any]) -> dict[str, float]:
        """
        Calculate centrality scores using PageRank-like algorithm.
        
        This is an INTERPRETIVE scoring algorithm that assigns importance
        based on graph topology.
        
        Args:
            graph: Graph with nodes and edges
            
        Returns:
            Dict mapping node IDs to centrality scores [0, 1]
        """
        # Build adjacency list
        adj = defaultdict(list)
        nodes = set()
        
        for edge in graph.get("edges", []):
            adj[edge["source"]].append(edge["target"])
            nodes.add(edge["source"])
            nodes.add(edge["target"])
        
        # Initialize scores
        scores = {node: 1.0 for node in nodes}
        damping = 0.85
        iterations = 10
        
        # Power iteration (PageRank algorithm)
        for _ in range(iterations):
            new_scores = {}
            for node in nodes:
                score = (1 - damping)
                for source in nodes:
                    if node in adj[source]:
                        out_count = len(adj[source]) or 1
                        score += damping * scores[source] / out_count
                new_scores[node] = score
            scores = new_scores
        
        # Normalize scores to [0, 1]
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def calculate_health_metrics(
        self,
        import_graph: dict[str, Any],
        cycles: list[dict] | None = None,
        hotspots: list[dict] | None = None,
        layers: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        """
        Calculate interpreted health metrics and grades.
        
        This method provides SUBJECTIVE health scoring based on
        architectural best practices. The scoring is opinionated
        and may not apply to all codebases.
        
        Args:
            import_graph: Import/dependency graph
            cycles: Pre-computed cycles (optional)
            hotspots: Pre-computed hotspots (optional)
            layers: Pre-computed layers (optional)
            
        Returns:
            Dict with health scores, grades, and metrics
        """
        # Calculate graph density
        nodes_count = len(import_graph.get("nodes", []))
        edges_count = len(import_graph.get("edges", []))
        max_edges = nodes_count * (nodes_count - 1) if nodes_count > 1 else 1
        density = edges_count / max_edges if max_edges > 0 else 0
        
        # INTERPRETATION: Calculate health score
        health_score = 100
        
        # SUBJECTIVE PENALTY: Penalize for cycles
        if cycles:
            cycle_penalty = min(len(cycles) * 5, 30)
            health_score -= cycle_penalty
        
        # SUBJECTIVE PENALTY: Penalize for high density (too coupled)
        if density > 0.3:
            density_penalty = min((density - 0.3) * 100, 20)
            health_score -= density_penalty
        
        # SUBJECTIVE PENALTY: Penalize for hotspots with very high degree
        if hotspots and hotspots[0]["in_degree"] > 50:
            hotspot_penalty = min(hotspots[0]["in_degree"] // 10, 20)
            health_score -= hotspot_penalty
        
        # INTERPRETATION: Assign letter grade
        health_grade = (
            "A" if health_score >= 90
            else "B" if health_score >= 80
            else "C" if health_score >= 70
            else "D" if health_score >= 60
            else "F"
        )
        
        # INTERPRETATION: Calculate fragility score (0-100, higher is worse)
        fragility = 0
        
        # Hotspots increase fragility
        if hotspots:
            top_hotspot_score = hotspots[0]["score"]
            fragility += min(top_hotspot_score * 10, 40)
        
        # Cycles increase fragility
        if cycles:
            fragility += min(len(cycles) * 3, 30)
        
        # High coupling increases fragility
        fragility += min(density * 100, 30)
        
        return {
            "health_score": max(health_score, 0),
            "health_grade": health_grade,
            "fragility_score": min(fragility, 100),
            "density": density,
            "cycle_free": len(cycles) == 0 if cycles else True,
            "well_layered": len(layers) > 2 and max(layers.keys()) < 10 if layers else False,
            "loosely_coupled": density < 0.2,
            "no_god_objects": not hotspots or hotspots[0]["in_degree"] < 30,
        }
    
    def generate_recommendations(
        self,
        import_graph: dict[str, Any],
        cycles: list[dict] | None = None,
        hotspots: list[dict] | None = None,
        layers: dict[str, list[str]] | None = None,
    ) -> list[str]:
        """
        Generate actionable recommendations based on graph analysis.
        
        These are OPINIONATED suggestions based on common architectural
        best practices. They may not apply to all projects.
        
        Args:
            import_graph: Import/dependency graph
            cycles: Pre-computed cycles (optional)
            hotspots: Pre-computed hotspots (optional)
            layers: Pre-computed layers (optional)
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Calculate density for recommendations
        nodes_count = len(import_graph.get("nodes", []))
        edges_count = len(import_graph.get("edges", []))
        max_edges = nodes_count * (nodes_count - 1) if nodes_count > 1 else 1
        density = edges_count / max_edges if max_edges > 0 else 0
        
        # INTERPRETATION: Generate recommendations
        if cycles and len(cycles) > 0:
            recommendations.append(
                f"Break {len(cycles)} dependency cycles to improve maintainability"
            )
        
        if density > 0.3:
            recommendations.append(
                "Reduce coupling between modules (current density: {:.2f})".format(
                    density
                )
            )
        
        if hotspots and len(hotspots) > 0 and hotspots[0]["in_degree"] > 30:
            recommendations.append(
                f"Refactor hotspot '{hotspots[0]['id']}' with {hotspots[0]['in_degree']} dependencies"
            )
        
        if layers and len(layers) <= 2:
            recommendations.append(
                "Consider introducing more architectural layers for better separation"
            )
        
        return recommendations
    
    def summarize(
        self,
        import_graph: dict[str, Any],
        call_graph: dict[str, Any] | None = None,
        cycles: list[dict] | None = None,
        hotspots: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Generate comprehensive INTERPRETED summary of graph analysis.
        
        This method combines objective metrics with subjective scoring
        and recommendations. It's designed for teams that want actionable
        insights beyond raw data.
        
        Args:
            import_graph: Import/dependency graph
            call_graph: Optional call graph
            cycles: Pre-computed cycles (optional)
            hotspots: Pre-computed hotspots (optional)
            
        Returns:
            Summary dict with metrics, health scores, and recommendations
        """
        from theauditor.graph.analyzer import XGraphAnalyzer
        
        # Use base analyzer for pure algorithms
        analyzer = XGraphAnalyzer()
        
        # Get pure metrics
        summary = {
            "import_graph": {
                "nodes": len(import_graph.get("nodes", [])),
                "edges": len(import_graph.get("edges", [])),
            }
        }
        
        # Add call graph metrics if available
        if call_graph:
            summary["call_graph"] = {
                "nodes": len(call_graph.get("nodes", [])),
                "edges": len(call_graph.get("edges", [])),
            }
        
        # Calculate graph density
        nodes_count = len(import_graph.get("nodes", []))
        edges_count = len(import_graph.get("edges", []))
        max_edges = nodes_count * (nodes_count - 1) if nodes_count > 1 else 1
        density = edges_count / max_edges if max_edges > 0 else 0
        summary["import_graph"]["density"] = density
        
        # Add cycle metrics
        if cycles is None:
            cycles = analyzer.detect_cycles(import_graph)
        
        summary["cycles"] = {
            "total": len(cycles),
            "largest": cycles[0]["size"] if cycles else 0,
            "nodes_in_cycles": len(
                set(node for cycle in cycles for node in cycle["nodes"])
            ),
        }
        
        # Add hotspot metrics
        if hotspots is None:
            hotspots = self.rank_hotspots(import_graph, call_graph)
        
        summary["hotspots"] = {
            "top_5": [h["id"] for h in hotspots[:5]],
            "max_in_degree": max((h["in_degree"] for h in hotspots), default=0),
            "max_out_degree": max((h["out_degree"] for h in hotspots), default=0),
        }
        
        # Identify layers
        layers = analyzer.identify_layers(import_graph)
        summary["layers"] = {
            "count": len(layers),
            "distribution": {k: len(v) for k, v in layers.items()},
        }
        
        # Add INTERPRETED health metrics
        summary["health_metrics"] = self.calculate_health_metrics(
            import_graph, cycles, hotspots, layers
        )
        
        # Add INTERPRETED recommendations
        summary["recommendations"] = self.generate_recommendations(
            import_graph, cycles, hotspots, layers
        )
        
        return summary
    
    def interpret_graph_summary(self, graph_data: dict[str, Any]) -> dict[str, Any]:
        """
        Add interpretive labels to graph summary data.
        
        This method adds subjective interpretations to raw graph statistics,
        such as coupling levels and architectural insights.
        
        Args:
            graph_data: Raw graph summary from analyzer
            
        Returns:
            Enhanced summary with interpretive insights
        """
        # Get base statistics
        stats = graph_data.get("statistics", {})
        density = stats.get("graph_density", 0)
        hotspots = graph_data.get("top_hotspots", [])
        
        # Add interpretive insights
        insights = {
            "coupling_level": (
                "high" if density > 0.3 
                else "medium" if density > 0.1 
                else "low"
            ),
            "potential_god_objects": len([
                h for h in hotspots 
                if h.get("in_degree", 0) > 30
            ]),
            "highly_connected": len([
                h for h in hotspots 
                if h.get("total_connections", 0) > 20
            ]),
        }
        
        # Merge with original data
        graph_data["architectural_insights"] = insights
        
        return graph_data
    
    def calculate_impact_ratio(
        self,
        targets: list[str],
        all_impacted: set[str],
        total_nodes: int,
    ) -> float:
        """
        Calculate interpreted impact ratio for change analysis.
        
        This is a SUBJECTIVE metric that interprets the scope of impact
        as a ratio of total system size.
        
        Args:
            targets: Original target nodes
            all_impacted: All impacted nodes (targets + upstream + downstream)
            total_nodes: Total number of nodes in graph
            
        Returns:
            Impact ratio [0, 1]
        """
        if total_nodes == 0:
            return 0.0
        
        return len(all_impacted) / total_nodes


# Module-level function for backward compatibility
def check_insights_available() -> bool:
    """Check if insights module is available (always True)."""
    return True


def create_insights(weights: dict[str, float] | None = None) -> GraphInsights:
    """
    Factory function to create GraphInsights instance.
    
    Args:
        weights: Optional custom weights for scoring
        
    Returns:
        GraphInsights instance
    """
    return GraphInsights(weights)