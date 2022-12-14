import Generation from "@shared/generation.type";
import _ from "lodash";

export const deleteQuestionOptimistic = (current: Generation, questionId: number) => {
    // remove current question from quiz data
    _.remove(current.questions, (q) => q.id === questionId);

    return current;
}

export const deleteAnswerOptimistic = (current: Generation, questionId: number, answerId: number) => {
    const q = _.find(current.questions, { id: questionId })!;

    // remove answer choice from quiz data
    _.remove(q.answers, (a) => a.id === answerId);

    return current;
}
