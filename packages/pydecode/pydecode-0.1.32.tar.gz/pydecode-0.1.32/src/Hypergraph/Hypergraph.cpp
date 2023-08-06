// Copyright [2013] Alexander Rush

#include <typeinfo>
#include <vector>

#include "Hypergraph/Hypergraph.h"

int Hypergraph::ID = 0;

HEdge Hypergraph::add_edge(const vector<HNode> &nodes)  {
  assert(lock_);
  Hyperedge *edge = new Hyperedge(creating_node_, nodes);
  creating_node_->add_edge(edge);
  temp_edges_.push_back(edge);
  return edge;
}

HNode Hypergraph::start_node() {
  terminal_lock_ = false;
  lock_ = true;
  creating_node_ = new Hypernode();
  creating_node_->set_id(temp_nodes_.size());
  temp_nodes_.push_back(creating_node_);
  return creating_node_;
}

bool Hypergraph::end_node() {
  assert(lock_);
  lock_ = false;

  // Remove this node if it has no edges.
  if (creating_node_->edges().size() == 0) {
    creating_node_->set_id(-1);
    temp_nodes_.pop_back();
    return false;
  } else {
    return true;
  }
}

HNode Hypergraph::add_terminal_node() {
  assert(terminal_lock_);
  Hypernode *node = new Hypernode();
  node->set_id(temp_nodes_.size());
  temp_nodes_.push_back(node);
  return temp_nodes_[temp_nodes_.size() - 1];
}

void Hypergraph::fill() {
  vector<bool> reachable_nodes(temp_nodes_.size(), false);
  vector<bool> reachable_edges(temp_edges_.size(), false);

  // Mark the reachable temp edges and nodes.
  for (int i = temp_edges_.size() - 1; i >= 0; --i) {
    HEdge edge = temp_edges_[i];
    if (edge->head_node()->id() == root()->id()) {
      reachable_nodes[edge->head_node()->id()] = true;
    }
    if (reachable_nodes[edge->head_node()->id()]) {
      reachable_edges[i] = true;
      foreach (HNode node, edge->tail_nodes()) {
        reachable_nodes[node->id()] = true;
      }
    }
  }

  // Relabel edges and nodes.
  int node_count = 0;
  for (uint i = 0; i < reachable_nodes.size(); ++i) {
    if (reachable_nodes[i]) {
      temp_nodes_[i]->set_id(node_count);
      nodes_.push_back(temp_nodes_[i]);
      node_count++;
    } else {
      temp_nodes_[i]->set_id(-1);
    }
  }
  int edge_count = 0;
  for (uint i = 0; i < reachable_edges.size(); ++i) {
    if (reachable_edges[i]) {
      temp_edges_[i]->set_id(edge_count);
      edges_.push_back(temp_edges_[i]);
      edge_count++;
    } else {
      temp_edges_[i]->set_id(-1);
    }
  }
}
