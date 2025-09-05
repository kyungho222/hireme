import React from 'react';
import { FiUser, FiMail, FiCheck, FiX, FiClock, FiTrendingUp } from 'react-icons/fi';
import * as S from '../styles/StatsStyles';

const StatsSection = ({ stats, onSendMail }) => {
  const statCards = [
    {
      variant: 'total',
      icon: <FiUser />,
      value: stats.total,
      label: '총 지원자',
      percentage: '100%',
      mailType: null
    },
    {
      variant: 'document_passed',
      icon: <FiCheck />,
      value: stats.document_passed || 0,
      label: '서류합격',
      percentage: stats.total > 0 ? `${Math.round(((stats.document_passed || 0) / stats.total) * 100)}%` : '0%',
      mailType: 'document_passed'
    },
    {
      variant: 'final_passed',
      icon: <FiTrendingUp />,
      value: stats.final_passed || 0,
      label: '최종합격',
      percentage: stats.total > 0 ? `${Math.round(((stats.final_passed || 0) / stats.total) * 100)}%` : '0%',
      mailType: 'final_passed'
    },
    {
      variant: 'waiting',
      icon: <FiClock />,
      value: stats.waiting,
      label: '보류',
      percentage: stats.total > 0 ? `${Math.round((stats.waiting / stats.total) * 100)}%` : '0%',
      mailType: null
    },
    {
      variant: 'rejected',
      icon: <FiX />,
      value: stats.rejected,
      label: '불합격',
      percentage: stats.total > 0 ? `${Math.round((stats.rejected / stats.total) * 100)}%` : '0%',
      mailType: 'rejected'
    }
  ];

  return (
    <S.StatsGrid>
      {statCards.map((card, index) => (
        <S.StatCard
          key={`${card.variant}-${card.value}`}
          $variant={card.variant}
        >
          {card.mailType && (
            <S.MailButton
              onClick={() => onSendMail(card.mailType)}
              disabled={card.value === 0}
              title={`${card.label}자들에게 메일 발송`}
            >
              <FiMail size={12} />
              메일
            </S.MailButton>
          )}
          <S.StatIcon>
            {card.icon}
          </S.StatIcon>
          <S.StatContent>
            <S.StatValue>
              {card.value}
            </S.StatValue>
            <S.StatLabel>{card.label}</S.StatLabel>
            <S.StatPercentage>
              {card.percentage}
            </S.StatPercentage>
          </S.StatContent>
        </S.StatCard>
      ))}
    </S.StatsGrid>
  );
};

export default StatsSection;
