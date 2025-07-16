"""
Response Aggregator Service
Combines and processes responses from multiple AI agents and services
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import aiofiles

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    TEXT = "text"
    CODE = "code"
    DATA = "data"
    ERROR = "error"
    STATUS = "status"

@dataclass
class AgentResponse:
    agent_id: str
    agent_type: str
    response_type: ResponseType
    content: Any
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    processing_time: float = 0.0

@dataclass
class AggregatedResponse:
    request_id: str
    responses: List[AgentResponse]
    combined_result: Any
    summary: str
    confidence_score: float
    processing_time: float
    timestamp: datetime
    status: str = "completed"

class ResponseAggregator:
    def __init__(self):
        self.aggregation_strategies = {
            "majority_vote": self._majority_vote_aggregation,
            "weighted_average": self._weighted_average_aggregation,
            "consensus": self._consensus_aggregation,
            "hierarchical": self._hierarchical_aggregation,
            "custom": self._custom_aggregation
        }
        
        self.agent_weights = {
            "requirements_analyst": 1.0,
            "architecture_designer": 1.2,
            "frontend_developer": 1.0,
            "backend_developer": 1.0,
            "database_designer": 1.0,
            "security_specialist": 1.3,
            "testing_engineer": 1.1,
            "performance_optimizer": 1.0,
            "deployment_engineer": 1.0,
            "quality_assurance": 1.2
        }

    async def aggregate_responses(
        self,
        request_id: str,
        responses: List[AgentResponse],
        strategy: str = "hierarchical"
    ) -> AggregatedResponse:
        """Aggregate multiple agent responses into a single result"""
        start_time = datetime.now()
        
        try:
            # Validate responses
            if not responses:
                raise ValueError("No responses to aggregate")
            
            # Group responses by type
            grouped_responses = self._group_responses_by_type(responses)
            
            # Apply aggregation strategy
            if strategy in self.aggregation_strategies:
                combined_result = await self.aggregation_strategies[strategy](grouped_responses)
            else:
                combined_result = await self._default_aggregation(grouped_responses)
            
            # Generate summary
            summary = await self._generate_summary(responses, combined_result)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(responses)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AggregatedResponse(
                request_id=request_id,
                responses=responses,
                combined_result=combined_result,
                summary=summary,
                confidence_score=confidence_score,
                processing_time=processing_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Response aggregation failed: {e}")
            return AggregatedResponse(
                request_id=request_id,
                responses=responses,
                combined_result=None,
                summary=f"Aggregation failed: {str(e)}",
                confidence_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
                status="failed"
            )

    def _group_responses_by_type(self, responses: List[AgentResponse]) -> Dict[ResponseType, List[AgentResponse]]:
        """Group responses by their type"""
        grouped = {}
        for response in responses:
            if response.response_type not in grouped:
                grouped[response.response_type] = []
            grouped[response.response_type].append(response)
        return grouped

    async def _majority_vote_aggregation(self, grouped_responses: Dict[ResponseType, List[AgentResponse]]) -> Any:
        """Aggregate using majority vote strategy"""
        combined_result = {}
        
        for response_type, responses in grouped_responses.items():
            if response_type == ResponseType.TEXT:
                # For text responses, use majority vote on key points
                combined_result[response_type.value] = await self._majority_vote_text(responses)
            elif response_type == ResponseType.CODE:
                # For code responses, combine and validate
                combined_result[response_type.value] = await self._combine_code_responses(responses)
            elif response_type == ResponseType.DATA:
                # For data responses, merge and deduplicate
                combined_result[response_type.value] = await self._merge_data_responses(responses)
            else:
                # For other types, use weighted average
                combined_result[response_type.value] = await self._weighted_average_responses(responses)
        
        return combined_result

    async def _weighted_average_aggregation(self, grouped_responses: Dict[ResponseType, List[AgentResponse]]) -> Any:
        """Aggregate using weighted average strategy"""
        combined_result = {}
        
        for response_type, responses in grouped_responses.items():
            combined_result[response_type.value] = await self._weighted_average_responses(responses)
        
        return combined_result

    async def _consensus_aggregation(self, grouped_responses: Dict[ResponseType, List[AgentResponse]]) -> Any:
        """Aggregate using consensus strategy"""
        combined_result = {}
        
        for response_type, responses in grouped_responses.items():
            # Find common elements across all responses
            consensus_result = await self._find_consensus(responses)
            combined_result[response_type.value] = consensus_result
        
        return combined_result

    async def _hierarchical_aggregation(self, grouped_responses: Dict[ResponseType, List[AgentResponse]]) -> Any:
        """Aggregate using hierarchical strategy based on agent importance"""
        combined_result = {}
        
        # Sort responses by agent weight
        all_responses = []
        for responses in grouped_responses.values():
            all_responses.extend(responses)
        
        sorted_responses = sorted(
            all_responses,
            key=lambda r: self.agent_weights.get(r.agent_type, 1.0),
            reverse=True
        )
        
        # Process responses hierarchically
        for response in sorted_responses:
            if response.response_type == ResponseType.CODE:
                if "code" not in combined_result:
                    combined_result["code"] = {}
                combined_result["code"][response.agent_type] = response.content
            elif response.response_type == ResponseType.TEXT:
                if "text" not in combined_result:
                    combined_result["text"] = {}
                combined_result["text"][response.agent_type] = response.content
            elif response.response_type == ResponseType.DATA:
                if "data" not in combined_result:
                    combined_result["data"] = {}
                combined_result["data"][response.agent_type] = response.content
        
        return combined_result

    async def _custom_aggregation(self, grouped_responses: Dict[ResponseType, List[AgentResponse]]) -> Any:
        """Custom aggregation strategy"""
        # This can be customized based on specific requirements
        return await self._hierarchical_aggregation(grouped_responses)

    async def _default_aggregation(self, grouped_responses: Dict[ResponseType, List[AgentResponse]]) -> Any:
        """Default aggregation strategy"""
        return await self._hierarchical_aggregation(grouped_responses)

    async def _majority_vote_text(self, responses: List[AgentResponse]) -> str:
        """Apply majority vote to text responses"""
        if not responses:
            return ""
        
        # Extract key points from each response
        key_points = []
        for response in responses:
            if isinstance(response.content, str):
                # Simple key point extraction (can be enhanced with NLP)
                points = response.content.split('.')
                key_points.extend([point.strip() for point in points if point.strip()])
        
        # Count occurrences and find majority
        point_counts = {}
        for point in key_points:
            point_counts[point] = point_counts.get(point, 0) + 1
        
        # Return points that appear in majority of responses
        majority_threshold = len(responses) / 2
        majority_points = [point for point, count in point_counts.items() if count >= majority_threshold]
        
        return '. '.join(majority_points)

    async def _combine_code_responses(self, responses: List[AgentResponse]) -> Dict[str, Any]:
        """Combine code responses from multiple agents"""
        combined_code = {}
        
        for response in responses:
            if isinstance(response.content, dict):
                # If content is already structured
                for key, value in response.content.items():
                    if key not in combined_code:
                        combined_code[key] = []
                    combined_code[key].append({
                        "content": value,
                        "agent": response.agent_type,
                        "confidence": response.confidence
                    })
            elif isinstance(response.content, str):
                # If content is a string, treat as a single file
                if "main" not in combined_code:
                    combined_code["main"] = []
                combined_code["main"].append({
                    "content": response.content,
                    "agent": response.agent_type,
                    "confidence": response.confidence
                })
        
        return combined_code

    async def _merge_data_responses(self, responses: List[AgentResponse]) -> Dict[str, Any]:
        """Merge data responses and remove duplicates"""
        merged_data = {}
        
        for response in responses:
            if isinstance(response.content, dict):
                for key, value in response.content.items():
                    if key not in merged_data:
                        merged_data[key] = value
                    elif isinstance(value, list) and isinstance(merged_data[key], list):
                        # Merge lists and remove duplicates
                        merged_data[key] = list(set(merged_data[key] + value))
                    elif isinstance(value, dict) and isinstance(merged_data[key], dict):
                        # Merge dictionaries
                        merged_data[key].update(value)
        
        return merged_data

    async def _weighted_average_responses(self, responses: List[AgentResponse]) -> Any:
        """Calculate weighted average of responses"""
        if not responses:
            return None
        
        total_weight = 0
        weighted_sum = 0
        
        for response in responses:
            weight = self.agent_weights.get(response.agent_type, 1.0) * response.confidence
            total_weight += weight
            
            if isinstance(response.content, (int, float)):
                weighted_sum += response.content * weight
            elif isinstance(response.content, str):
                # For text, use confidence as weight
                weighted_sum += len(response.content) * weight
        
        if total_weight == 0:
            return responses[0].content if responses else None
        
        if isinstance(responses[0].content, (int, float)):
            return weighted_sum / total_weight
        else:
            # For non-numeric content, return the highest confidence response
            return max(responses, key=lambda r: r.confidence).content

    async def _find_consensus(self, responses: List[AgentResponse]) -> Any:
        """Find consensus among responses"""
        if not responses:
            return None
        
        if len(responses) == 1:
            return responses[0].content
        
        # For text responses, find common phrases
        if isinstance(responses[0].content, str):
            return await self._find_text_consensus(responses)
        
        # For other types, return the most common response
        content_counts = {}
        for response in responses:
            content_str = str(response.content)
            content_counts[content_str] = content_counts.get(content_str, 0) + 1
        
        # Return the most common content
        most_common = max(content_counts.items(), key=lambda x: x[1])
        return most_common[0]

    async def _find_text_consensus(self, responses: List[AgentResponse]) -> str:
        """Find consensus in text responses"""
        # Simple consensus finding (can be enhanced with NLP)
        all_text = " ".join([r.content for r in responses if isinstance(r.content, str)])
        
        # Find common words/phrases
        words = all_text.lower().split()
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 characters
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Return words that appear in majority of responses
        majority_threshold = len(responses) / 2
        consensus_words = [word for word, count in word_counts.items() if count >= majority_threshold]
        
        return " ".join(consensus_words)

    async def _generate_summary(self, responses: List[AgentResponse], combined_result: Any) -> str:
        """Generate a summary of the aggregation process"""
        summary_parts = []
        
        # Count responses by type
        type_counts = {}
        for response in responses:
            response_type = response.response_type.value
            type_counts[response_type] = type_counts.get(response_type, 0) + 1
        
        summary_parts.append(f"Processed {len(responses)} responses from {len(type_counts)} types:")
        for response_type, count in type_counts.items():
            summary_parts.append(f"- {response_type}: {count}")
        
        # Add confidence information
        avg_confidence = sum(r.confidence for r in responses) / len(responses) if responses else 0
        summary_parts.append(f"Average confidence: {avg_confidence:.2f}")
        
        # Add result summary
        if isinstance(combined_result, dict):
            summary_parts.append(f"Combined result contains {len(combined_result)} sections")
        else:
            summary_parts.append(f"Combined result type: {type(combined_result).__name__}")
        
        return " | ".join(summary_parts)

    def _calculate_confidence_score(self, responses: List[AgentResponse]) -> float:
        """Calculate overall confidence score"""
        if not responses:
            return 0.0
        
        # Weighted average of confidence scores
        total_weight = 0
        weighted_confidence = 0
        
        for response in responses:
            weight = self.agent_weights.get(response.agent_type, 1.0)
            total_weight += weight
            weighted_confidence += response.confidence * weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0

    async def validate_aggregated_response(self, aggregated_response: AggregatedResponse) -> bool:
        """Validate the aggregated response"""
        try:
            # Check if we have responses
            if not aggregated_response.responses:
                return False
            
            # Check confidence threshold
            if aggregated_response.confidence_score < 0.5:
                return False
            
            # Check if combined result is not None
            if aggregated_response.combined_result is None:
                return False
            
            # Check processing time is reasonable
            if aggregated_response.processing_time > 300:  # 5 minutes
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            return False

# Global instance
response_aggregator = ResponseAggregator()