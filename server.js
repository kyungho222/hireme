require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const Talent = require('./models/Talent');
const axios = require('axios');

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const GROQ_API_URL = 'https://api.groq.com/v1/chat/completions';

const app = express();

// 미들웨어 설정
app.use(cors());
app.use(express.json());

// MongoDB 연결
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/hireme')
  .then(() => console.log('MongoDB Connected'))
  .catch(err => console.error('MongoDB Connection Error:', err));

// Groq API를 사용한 인재 분석
async function analyzeWithGroq(talentData) {
  try {
    const prompt = `
다음 인재 정보를 분석하여 주요 특징과 강점을 5개의 태그로 추출해주세요:

이름: ${talentData.name}
직무: ${talentData.position}
경력: ${talentData.experience}
기술 스택: ${talentData.skills.join(', ')}
자기 소개: ${talentData.description}

태그는 다음과 같은 형식으로 작성해주세요:
- 기술_전문성
- 경험_수준
- 역량_특징
- 성장_가능성
- 직무_적합성

각 태그는 한글로 작성하고, 쉼표로 구분해주세요.
`;

    const response = await axios.post(GROQ_API_URL, {
      model: "llama2-70b-4096",
      messages: [
        {
          role: "system",
          content: "당신은 전문적인 인재 분석가입니다. 주어진 정보를 바탕으로 인재의 특징과 강점을 정확하게 분석해주세요."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      temperature: 0.5,
      max_tokens: 1000
    }, {
      headers: {
        'Authorization': `Bearer ${GROQ_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    const aiTags = response.data.choices[0].message.content
      .split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0);

    return aiTags;
  } catch (error) {
    console.error('AI 분석 중 오류 발생:', error);
    return [];
  }
}

// 인재 정보 등록
app.post('/api/recommendations', async (req, res) => {
  try {
    const talentData = req.body;
    
    // AI 분석 수행
    const aiTags = await analyzeWithGroq(talentData);
    
    // 기본 매칭 점수 계산 (예시: 태그 수에 따라)
    const matchRate = Math.min(Math.round((aiTags.length / 5) * 100), 100);
    
    const talent = new Talent({
      ...talentData,
      aiTags,
      matchRate,
      rating: 0 // 초기 평점
    });
    
    await talent.save();
    res.status(201).json(talent);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 인재 목록 조회
app.get('/api/recommendations', async (req, res) => {
  try {
    const talents = await Talent.find().sort({ createdAt: -1 });
    res.json(talents);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 관리자용 인재 목록 조회
app.get('/api/talents', async (req, res) => {
  try {
    const talents = await Talent.find().sort({ createdAt: -1 });
    res.json(talents);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// AI 챗봇을 통한 인재 검색
app.post('/api/talents/search', async (req, res) => {
  try {
    const { query } = req.body;
    
    // Groq를 통한 요구사항 분석
    const response = await axios.post(GROQ_API_URL, {
      model: "llama2-70b-4096",
      messages: [
        {
          role: "system",
          content: "당신은 채용 전문가입니다. 주어진 요구사항에서 핵심적인 키워드와 특성을 추출해주세요."
        },
        {
          role: "user",
          content: `다음 채용 요구사항에서 5개의 핵심 키워드를 추출해주세요: ${query}`
        }
      ],
      temperature: 0.3,
      max_tokens: 1000
    }, {
      headers: {
        'Authorization': `Bearer ${GROQ_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    const searchTags = response.data.choices[0].message.content
      .split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0);

    // 태그 기반으로 인재 검색
    const talents = await Talent.find({
      $or: [
        { aiTags: { $in: searchTags } },
        { skills: { $in: searchTags } },
        { position: { $in: searchTags } }
      ]
    }).sort({ matchRate: -1 });

    // 매칭 점수 재계산
    const talentsWithUpdatedScore = talents.map(talent => {
      const matchingTags = talent.aiTags.filter(tag => 
        searchTags.some(searchTag => 
          tag.toLowerCase().includes(searchTag.toLowerCase())
        )
      ).length;
      
      const newMatchRate = Math.min(Math.round((matchingTags / searchTags.length) * 100), 100);
      
      return {
        ...talent.toObject(),
        matchRate: newMatchRate
      };
    });

    res.json(talentsWithUpdatedScore);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});