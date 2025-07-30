const mongoose = require('mongoose');

const talentSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  position: {
    type: String,
    required: true
  },
  experience: {
    type: String,
    required: true
  },
  location: {
    type: String,
    required: true
  },
  skills: [{
    type: String,
    required: true
  }],
  aiTags: [{
    type: String
  }],
  description: {
    type: String,
    required: true
  },
  matchRate: {
    type: Number,
    default: 0
  },
  avatar: {
    type: String,
    default: 'https://via.placeholder.com/60'
  },
  rating: {
    type: Number,
    default: 0
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Talent', talentSchema);