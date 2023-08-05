from mamba import describe, context
from sure import expect


class FizzBuzz(object):

    def play(self, number):
        result = ''
        if self._is_fizz(number):
            result += 'Fizz'
        if self._is_buzz(number):
            result += 'Buzz'
        if not result:
            result = str(number)
        return result

    def _is_fizz(self, number):
        return number % 3 == 0 or '3' in str(number)

    def _is_buzz(self, number):
        return number % 5 == 0


with describe(FizzBuzz) as _:

    def it_returns_same_number_if_is_not_multiple_of_3_or_5():
        result = _.subject.play(1)

        expect(result).to.be.equal('1')

    def it_returns_Fizz_if_is_multiple_of_3():
        result = _.subject.play(3)

        expect(result).to.be.equal('Fizz')

    def it_returns_Buzz_if_is_multiple_of_5():
        result = _.subject.play(5)

        expect(result).to.be.equal('Buzz')

    def it_returns_FizzBuzz_if_is_multiple_of_3_and_5():
        result = _.subject.play(15)

        expect(result).to.be.equal('FizzBuzz')

    with context('when changing requirements'):
        def it_returns_Fizz_if_contains_3():
            result = _.subject.play(13)

            expect(result).to.be.equal('Fizz')

        def it_returns_Buzz_if_contains_5():
            result = _.subject.play(25)

            expect(result).to.be.equal('Buzz')


